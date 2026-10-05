#!/bin/bash
# usage: [PORT=4010] run.sh <harness> <prompt> <timeout_s> <name>   -> out/<name>.{out,err,meta}
H=$1; P=$2; T=$3; N=$4; E=/workspace/harness-faults; PORT=${PORT:-4010}
export PATH=/opt/node22/bin:$PATH
mkdir -p $E/out $E/work/$N $E/cfg/cc_$N $E/cfg/oc_$N/{data,config,state} $E/cfg/codex_$N
sed "s/4010/$PORT/" $E/cfg/codex/config.toml > $E/cfg/codex_$N/config.toml
sed "s/4010/$PORT/" $E/cfg/oc/opencode.json > $E/cfg/oc_$N/opencode.json
O=$E/out/$N
cd $E/work/$N
CLEAN="env -u ANTHROPIC_API_KEY -u ANTHROPIC_BASE_URL -u OPENAI_API_KEY -u OPENAI_BASE_URL"
start=$(date +%s.%N)
case $H in
 cc) $CLEAN CLAUDE_CONFIG_DIR=$E/cfg/cc_$N ANTHROPIC_BASE_URL=http://127.0.0.1:$PORT ANTHROPIC_API_KEY=sk-ant-test CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_AUTOUPDATER=1 IS_SANDBOX=1 \
       timeout $T $E/node_modules/.bin/claude -p "$P" --model claude-sonnet-5 --output-format json --dangerously-skip-permissions > $O.out 2> $O.err < /dev/null ;;
 codex) $CLEAN CODEX_HOME=$E/cfg/codex_$N MOCK_API_KEY=x timeout $T $E/node_modules/.bin/codex exec --skip-git-repo-check --json --dangerously-bypass-approvals-and-sandbox "$P" > $O.out 2> $O.err < /dev/null ;;
 oc) $CLEAN OPENCODE_CONFIG=$E/cfg/oc_$N/opencode.json XDG_DATA_HOME=$E/cfg/oc_$N/data XDG_CONFIG_HOME=$E/cfg/oc_$N/config XDG_CACHE_HOME=$E/cfg/oc_cache XDG_STATE_HOME=$E/cfg/oc_$N/state OPENCODE_DISABLE_AUTOUPDATE=1 \
       timeout $T $E/node_modules/.bin/opencode run --model mock/mock-model --format json "$P" > $O.out 2> $O.err < /dev/null ;;
esac
rc=$?
end=$(date +%s.%N)
python3 -c "print('rc=$rc secs=%.1f' % ($end-$start))" > $O.meta
ls -A $E/work/$N >> $O.meta
