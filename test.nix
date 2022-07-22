{ nixpkgs, self, system }:
with import (nixpkgs + "/nixos/lib/testing-python.nix") { inherit system; };
makeTest {
  nodes = {
    machine = { config, pkgs, ... }: {
      imports = [ self.nixosModules.default ];

      nixpkgs.overlays = [ self.overlays.default ];

      services.proximity_matcher_webservice = {
        enable = true;
        hashesPicklePath = "/var/lib/proximity_matcher_webservice/hashes.pickle";
        hashesPath = "/var/lib/proximity_matcher_webservice/hashes";
      };

      systemd.services.proximity_matcher_webservice_setup = {
        wantedBy = [ "multi-user.target" ];
        before = [ "proximity_matcher_webservice.service" ];
        script = ''
          mkdir -p /var/lib/proximity_matcher_webservice
          cd /var/lib/proximity_matcher_webservice
          mkdir testfiles
          cp ${config.services.proximity_matcher_webservice.package.src}/LICENSE testfiles
          ${pkgs.proximity_matcher_webservice}/bin/prepare_tlsh_hashes -i testfiles -o hashes
          ${pkgs.proximity_matcher_webservice}/bin/create-vpt-pickle -i hashes -o hashes.pickle
        '';
      };
    };
  };

  testScript = ''
    machine.start()
    machine.wait_for_open_port(5000)
    machine.succeed(r"""curl -s http://127.0.0.1:5000/tlsh/$(cat /var/lib/proximity_matcher_webservice/hashes) | ${pkgs.jq}/bin/jq -cS . | grep -E '^{"distance":0,"match":true,"tlsh":"'"$(cat /var/lib/proximity_matcher_webservice/hashes)"'"}$'""")
  '';
}
