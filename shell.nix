{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.shellcheck
    pkgs.tig
    pkgs.ncdu
  ];

  shellHook = ''
    venv_dir=.venv/ansible-doctor
    if [ ! -d $venv_dir ]; then
      python -m venv $venv_dir
      $venv_dir/bin/pip install --upgrade pip
      $venv_dir/bin/pip --require-virtualenv  install -r tools/dev/requirements_doctor.txt
    fi

    venv_dir=.venv/antsibull
    if [ ! -d $venv_dir ]; then
      python -m venv $venv_dir
      $venv_dir/bin/pip install --upgrade pip
      $venv_dir/bin/pip --require-virtualenv  install -r tools/dev/requirements_antsibull.txt
    fi

    # 1st .venv dir for ansible-navigator etc.
    venv_dir=.venv/ansible-oracle
    if [ ! -d $venv_dir ]; then
      python -m venv $venv_dir
      $venv_dir/bin/pip install --upgrade pip
      $venv_dir/bin/pip --require-virtualenv  install -r tools/dev/requirements_dev.txt
    fi
    . $venv_dir/bin/activate
  '';
}
