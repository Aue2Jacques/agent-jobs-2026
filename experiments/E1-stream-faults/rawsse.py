"""Minimal raw SSE fault server for faults aimock cannot express.
Scenario is chosen by a marker in the request text: RAW_NOFINISH, RAW_BODYSTALL, RAW_KEEPALIVE, RAW_INCOMPLETE.
Protocols: /v1/chat/completions (OpenAI chat), /v1/responses (OpenAI Responses), /v1/messages (Anthropic).
Non-streaming requests: stall cases hang; other fault cases get HTTP 500 (keeps the fault persistent).
Requests without a marker get a normal short reply 'RAW_PLAIN_OK'."""
import json, time, sys, threading, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
LOG=open(sys.argv[2] if len(sys.argv)>2 else "rawsse.log","a")
SCEN=["RAW_NOFINISH","RAW_BODYSTALL","RAW_KEEPALIVE","RAW_INCOMPLETE"]
def ev(name,obj): return (f"event: {name}\n" if name else "")+"data: "+json.dumps(obj)+"\n\n"
class H(BaseHTTPRequestHandler):
    protocol_version="HTTP/1.1"
    def log_message(self,*a): pass
    def chunk(self,s):
        b=s.encode(); self.wfile.write(b"%x\r\n"%len(b)+b+b"\r\n"); self.wfile.flush()
    def end(self): self.wfile.write(b"0\r\n\r\n"); self.wfile.flush()
    def do_GET(self):
        self.send_response(404); self.send_header("content-length","0"); self.end_headers()
    def do_POST(self):
        n=int(self.headers.get("content-length",0)); raw=self.rfile.read(n); body=json.loads(raw or b"{}")
        txt=raw.decode("utf-8","ignore")
        # only look at the last user turn so harness system prompts / history do not confuse matching
        sc=next((s for s in SCEN if s in txt),None)
        stream=body.get("stream",False)
        p=self.path.split("?")[0]
        LOG.write(json.dumps({"t":time.time(),"path":p,"stream":stream,"scenario":sc,"ua":self.headers.get("user-agent","")[:40]})+"\n"); LOG.flush()
        if not stream:
            if sc in ("RAW_BODYSTALL","RAW_KEEPALIVE"): time.sleep(900); return
            if sc: return self.err500()
            return self.plain_nonstream(p)
        self.send_response(200); self.send_header("content-type","text/event-stream"); self.send_header("transfer-encoding","chunked"); self.send_header("cache-control","no-cache"); self.end_headers()
        try:
            getattr(self,"s_"+{"/v1/chat/completions":"chat","/v1/responses":"resp","/v1/messages":"msg"}.get(p,"chat"))(sc)
        except (BrokenPipeError,ConnectionResetError): pass
    def err500(self):
        b=json.dumps({"error":{"message":"server error","type":"server_error"}}).encode()
        self.send_response(500); self.send_header("content-type","application/json"); self.send_header("content-length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def plain_nonstream(self,p):
        if p=="/v1/messages": o={"id":"msg_x","type":"message","role":"assistant","model":"m","content":[{"type":"text","text":"RAW_PLAIN_OK"}],"stop_reason":"end_turn","usage":{"input_tokens":1,"output_tokens":1}}
        else: o={"id":"c","object":"chat.completion","model":"m","choices":[{"index":0,"message":{"role":"assistant","content":"RAW_PLAIN_OK"},"finish_reason":"stop"}],"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}}
        b=json.dumps(o).encode(); self.send_response(200); self.send_header("content-type","application/json"); self.send_header("content-length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def tail(self,sc,ka):
        if sc=="RAW_BODYSTALL": time.sleep(900); return True
        if sc=="RAW_KEEPALIVE":
            for _ in range(90): time.sleep(10); self.chunk(ka)
            return True
        if sc=="RAW_NOFINISH": self.end(); return True
        return False
    # OpenAI chat completions
    def s_chat(self,sc):
        base={"id":"chatcmpl-raw","object":"chat.completion.chunk","created":int(time.time()),"model":"m"}
        self.chunk("data: "+json.dumps({**base,"choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":None}]})+"\n\n")
        text="RAW_PARTIAL this answer is cut" if sc else "RAW_PLAIN_OK"
        self.chunk("data: "+json.dumps({**base,"choices":[{"index":0,"delta":{"content":text},"finish_reason":None}]})+"\n\n")
        if self.tail(sc,": keepalive\n\n"): return
        self.chunk("data: "+json.dumps({**base,"choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":1,"completion_tokens":1,"total_tokens":2}})+"\n\ndata: [DONE]\n\n"); self.end()
    # OpenAI Responses
    def s_resp(self,sc):
        rid="resp_raw"; mid="msg_raw"
        r={"id":rid,"object":"response","created_at":int(time.time()),"model":"m","status":"in_progress","output":[]}
        self.chunk(ev("response.created",{"type":"response.created","response":r}))
        self.chunk(ev("response.output_item.added",{"type":"response.output_item.added","output_index":0,"item":{"type":"message","id":mid,"status":"in_progress","role":"assistant","content":[]}}))
        self.chunk(ev("response.content_part.added",{"type":"response.content_part.added","item_id":mid,"output_index":0,"content_index":0,"part":{"type":"output_text","text":"","annotations":[]}}))
        text="" if sc=="RAW_INCOMPLETE" else ("RAW_PARTIAL this answer is cut" if sc else "RAW_PLAIN_OK")
        if text: self.chunk(ev("response.output_text.delta",{"type":"response.output_text.delta","item_id":mid,"output_index":0,"content_index":0,"delta":text}))
        if sc=="RAW_KEEPALIVE": return self.tail(sc,": keepalive\n\n")
        if self.tail(sc,""): return
        item={"type":"message","id":mid,"status":"incomplete" if sc=="RAW_INCOMPLETE" else "completed","role":"assistant","content":[{"type":"output_text","text":text,"annotations":[]}]}
        self.chunk(ev("response.output_text.done",{"type":"response.output_text.done","item_id":mid,"output_index":0,"content_index":0,"text":text}))
        self.chunk(ev("response.output_item.done",{"type":"response.output_item.done","output_index":0,"item":item}))
        usage={"input_tokens":1,"output_tokens":0 if sc else 1,"total_tokens":1}
        if sc=="RAW_INCOMPLETE":
            self.chunk(ev("response.incomplete",{"type":"response.incomplete","response":{**r,"status":"incomplete","incomplete_details":{"reason":"max_output_tokens"},"output":[item],"usage":usage}}))
        else:
            self.chunk(ev("response.completed",{"type":"response.completed","response":{**r,"status":"completed","output":[item],"usage":usage}}))
        self.end()
    # Anthropic messages
    def s_msg(self,sc):
        self.chunk(ev("message_start",{"type":"message_start","message":{"id":"msg_raw","type":"message","role":"assistant","content":[],"model":"m","stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":1,"output_tokens":0}}}))
        self.chunk(ev("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}))
        text="RAW_PARTIAL this answer is cut" if sc else "RAW_PLAIN_OK"
        self.chunk(ev("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}))
        if sc=="RAW_KEEPALIVE": return self.tail(sc,ev("ping",{"type":"ping"}))
        if self.tail(sc,""): return
        self.chunk(ev("content_block_stop",{"type":"content_block_stop","index":0}))
        stop="max_tokens" if sc=="RAW_INCOMPLETE" else "end_turn"
        self.chunk(ev("message_delta",{"type":"message_delta","delta":{"stop_reason":stop,"stop_sequence":None},"usage":{"output_tokens":1}}))
        self.chunk(ev("message_stop",{"type":"message_stop"})); self.end()
ThreadingHTTPServer(("127.0.0.1",int(sys.argv[1])),H).serve_forever()
