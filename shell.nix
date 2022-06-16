let
  # Use `niv update` to update nixpkgs.
  # See https://github.com/nmattia/niv/
  sources = import ./nix/sources.nix;

  pkgs = import sources.nixpkgs { config.allowUnfree = true; overlays = []; };

  my-python = pkgs.python39.withPackages (p: with p; [
    click
    flask
    gevent
    gunicorn
    poetry
    pyyaml
    requests
    tlsh
  ]);

in
pkgs.mkShell {
  buildInputs = with pkgs; [
    my-python
  ];
}
