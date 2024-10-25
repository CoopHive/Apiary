with import <nixpkgs> { };

pkgs.mkShell {
  buildInputs = [
    python39
    darwin.apple_sdk.frameworks.Security
    darwin.apple_sdk.frameworks.SystemConfiguration
  ];
}

