ENV_PATH="${HOME}/AppData/Local/pypoetry/Cache/virtualenvs"

# Create a new environment or synchronize the existing one.
if envs=(${ENV_PATH}/poetry-*-py*) && [[ -d ${envs[0]} ]]; then
    echo "Sync existing environment ${envs[0]}"
    source "${envs[0]}/Scripts/activate"
    eval "~/.local/bin/poetry install --no-root"
    eval "~/.local/bin/poetry sync --no-root"
    deactivate

else
    echo "Create new environment under ${ENV_PATH}"
    eval "~/.local/bin/poetry install --no-root"
    eval "~/.local/bin/poetry sync --no-root"

fi
