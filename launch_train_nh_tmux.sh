#!/bin/bash

# ——— CONFIGURATION ———
SESSION_NAME="nhtrain"
CONDA_PROFILE="/software/u24/miniforge/24.7.1-0/etc/profile.d/conda.sh"
ENV_NAME="neuralhydrology"
CONFIG_FILE="config_hr_aorc.yml"
LOG_FILE="train.log"

# ——— 0) Clear any existing log ———
: > "$LOG_FILE"

# ——— 1) Disable tmux scrollback entirely ———
# Set history-limit to 0 so tmux keeps virtually no buffer
tmux set-option -g history-limit 0

# ——— 2) Start a new, detached tmux session running your job ———
# We rely on pipe-pane (below) to capture ALL output to disk.
tmux new-session -s "$SESSION_NAME" -d \
  "bash -lc 'source \"$CONDA_PROFILE\" && \
             conda activate \"$ENV_NAME\" && \
             date >> \"$LOG_FILE\" && \
             nh-run train --config-file \"$CONFIG_FILE\" >> \"$LOG_FILE\" 2>&1 && \
             date >> \"$LOG_FILE\"'"

# ——— 3) Immediately pipe *all* pane output into your log file ———
# tmux will forward everything to train.log and not hold it in memory.
tmux pipe-pane -t "$SESSION_NAME" 'cat >>'"$LOG_FILE"

echo "Launched session '$SESSION_NAME'. All output is streaming to $LOG_FILE"
