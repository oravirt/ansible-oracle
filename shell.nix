{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.wslu # needed only on WSL2
    pkgs.bashInteractive
    pkgs.bash-completion
    pkgs.python313
    pkgs.shellcheck
    pkgs.tig
    pkgs.ncdu
    # pkgs.packer
    pkgs.go-task
    pkgs.jq
    pkgs.yq
    pkgs.gh   # needed for renovate
    pkgs.renovate

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

    venv_dir=.venv/ansible-2.16
    if [ ! -d $venv_dir ]; then
      python -m venv $venv_dir
      $venv_dir/bin/pip install --upgrade pip
      $venv_dir/bin/pip --require-virtualenv  install -r tools/dev/requirements_dev_2.16.txt
    fi

    venv_dir=.venv/ansible-2.19
    if [ ! -d $venv_dir ]; then
      python -m venv $venv_dir
      $venv_dir/bin/pip install --upgrade pip
      $venv_dir/bin/pip --require-virtualenv  install -r tools/dev/requirements_dev_2.19.txt
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
