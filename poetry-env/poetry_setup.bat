set VER=3.13.7

cd %USERPROFILE%

rm -rf %USERPROFILE%/.pyenv
rm -rf %USERPROFILE%/.local
rm -rf %USERPROFILE%/pipx
rm -rf %USERPROFILE%/pyenv-win-master
rm -rf %USERPROFILE%/AppData/Local/pypoetry/*

curl -LO https://github.com/pyenv-win/pyenv-win/archive/master.zip --ssl-no-revoke
tar -xvzf master.zip
ren pyenv-win-master .pyenv
rm master.zip

setx PYENV %USERPROFILE%\.pyenv\pyenv-win\
setx PYENV_ROOT %USERPROFILE%\.pyenv\pyenv-win\
setx PYENV_HOME %USERPROFILE%\.pyenv\pyenv-win\

powershell -command  "[System.Environment]::SetEnvironmentVariable('Path', '', 'User')"
powershell -command "[System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + '\.pyenv\pyenv-win\bin;' + [System.Environment]::GetEnvironmentVariable('path', 'User'),'User')"
powershell -command "[System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + '\.pyenv\pyenv-win\shims;' + [System.Environment]::GetEnvironmentVariable('path', 'User'),'User')"
powershell -command "[System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + '\.local\bin;' + [System.Environment]::GetEnvironmentVariable('path', 'User'),'User')"

call %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv --version
call %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv install %VER%
call %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv global %VER%

call %USERPROFILE%\.pyenv\pyenv-win\versions\%VER%\python -m pip install --user pipx
call %USERPROFILE%\.pyenv\pyenv-win\versions\%VER%\python -m pipx install poetry --force

set python_path=%USERPROFILE%\.pyenv\pyenv-win\versions\%VER%;
