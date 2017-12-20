#!/bin/bash
url="http://127.0.0.1:8003/remote"
:<<!EOF!
curl -F "json_file=@$HOME/test.json" -F "bin_file=@$HOME/test.bin" "$url/upgrade.ComponentUpgradeApi.add_version/"
echo -e "\n"


curl -F '_params={"project_id":"57ff2e3a7ff63b1661dd0fbf","component_type":"gate"}' "$url/upgrade.ComponentUpgradeApi.check_upgrade/"
echo -e "\n"


curl -F '_params={}' "$url/upgrade.ComponentUpgradeApi.get_verison_by_filter/"
echo -e "\n"
!EOF!

curl -F '_params={"bin_file_id":"585a4bec3b75d512a0e839b8"}' "$url/upgrade.ComponentUpgradeApi.download_upgrade_file/"
echo -e "\n"

:<<!EOF!
curl -F '_params={"mobile":"18520870599", "password_token":"396ccceff13a6c91e83178048c6f2560"}' "$url/qduser.QdUserApi.login/"
echo -e "\n"


curl -F '_params={"aptm_id":"57ff2e3a7ff63b1661dd0fbf"}' "$url/gate_pass.GatePasswordPassApi.user_get_password/"
echo -e "\n"


curl -F '_params={"password":"545814"}' "$url/gate_pass.GatePasswordPassApi.gate_validate_password/"
echo -e "\n"
!EOF!