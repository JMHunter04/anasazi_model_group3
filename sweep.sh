#!/bin/bash
# sweep.sh: one-at-a-time parameter sweep for the Anasazi model.
#
# Usage (run from inside the model folder):
#   bash sweep.sh <parameter> <value1> <value2> ...
# Example:
#   bash sweep.sh harvest.adj 0.54484 0.62 0.70 1.0
#
# For each value it: edits props/model.props, runs the model, and saves
# NumberOfHousehold.csv as outputs/<parameter>_<value>.csv.
# The original model.props is always restored at the end, even if a run fails
# or you press Ctrl+C.

PARAM="$1"
shift
VALUES="$@"

if [ -z "$PARAM" ] || [ -z "$VALUES" ]; then
  echo "Usage: bash sweep.sh <parameter> <value1> <value2> ..."
  exit 1
fi

if ! grep -q "^${PARAM} *=" props/model.props; then
  echo "Parameter '$PARAM' not found in props/model.props. Check the spelling."
  exit 1
fi

mkdir -p outputs
cp props/model.props props/model.props.bak
trap 'cp props/model.props.bak props/model.props; rm -f props/model.props.bak; echo "model.props restored."' EXIT

for v in $VALUES; do
  sed -i "s/^${PARAM//./\\.} *=.*/${PARAM} = ${v}/" props/model.props
  echo "=== Running ${PARAM} = ${v} ($(date +%H:%M:%S)) ==="
  grep "^${PARAM} *=" props/model.props
      rm -f NumberOfHousehold.csv
  mpirun -bind-to none -n 1 ./bin/main.exe props/config.props props/model.props
  cp NumberOfHousehold.csv "outputs/${PARAM}_${v}.csv"
  echo "Saved outputs/${PARAM}_${v}.csv (last year: $(tail -1 NumberOfHousehold.csv))"
done

echo "Sweep finished."
