{
  description = "Webservice for proximity matching using TLSH and Vantage Point Trees";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }: ({
    overlays.default = import ./overlay.nix;
  }) // (
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = f: nixpkgs.lib.genAttrs supportedSystems (system: f system);
    in
    {
      packages = forAllSystems (system: rec {
        inherit (self.overlays.default null nixpkgs.legacyPackages.${system}) proximity_matcher_webservice;
        default = proximity_matcher_webservice;
      });
    }
  );
}
