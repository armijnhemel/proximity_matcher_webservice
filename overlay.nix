final: prev: rec {
  python3 = prev.python3.override {
    packageOverrides = final: prev:
      {
        py-tlsh = python3Packages.callPackage
          ({ buildPythonPackage, fetchPypi }: buildPythonPackage rec {
            pname = "py-tlsh";
            version = "4.7.2";

            src = fetchPypi {
              inherit pname version;
              sha256 = "sha256-W2lDz9k6FoZx8zuEgo3KNNJSJ4ve3KzyXL5xH9plXp8=";
            };
          })
          { };
      };
  };
  python3Packages = prev.recurseIntoAttrs python3.pkgs;

  proximity_matcher_webservice = python3Packages.callPackage
    ({ lib
     , buildPythonPackage
     , poetry-core
     , click
     , flask
     , gevent
     , gunicorn
     , py-tlsh
     , pyyaml
     , requests
     , python
     }: buildPythonPackage rec {
      pname = "proximity_matcher_webservice";
      version = "0.0.1";

      src = ./.;

      nativeBuildInputs = [ poetry-core ];
      propagatedBuildInputs = [ click flask gevent gunicorn py-tlsh pyyaml requests ];

      format = "pyproject";

      postInstall = ''
        install -m555 examples/software_heritage_licenses/prepare_tlsh_hashes.py $out/bin/prepare_tlsh_hashes
        install -m555 examples/software_heritage_licenses/test_licenses.py $out/bin/test_licenses
        install -m555 examples/software_heritage_licenses/walk_software_heritage_blobs.py $out/bin/walk_software_heritage_blobs
      '';

      # required for gunicorn (which is called as an executable from python) to work
      makeWrapperArgs = [ "--set PYTHONPATH $out${python.sitePackages}:$PYTHONPATH" ];

      passthru = {
        # required for the module to use the correct python modules
        python = python.withPackages (lib.const (propagatedBuildInputs ++ (lib.singleton proximity_matcher_webservice)));
      };

      meta = with lib; {
        description = "Webservice for proximity matching using TLSH and Vantage Point Trees";
        homepage = "https://github.com/armijnhemel/proximity_matcher_webservice";
        license = licenses.asl20;
        platforms = platforms.linux;
      };
    })
    { };
}
