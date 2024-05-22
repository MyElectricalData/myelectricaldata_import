# CHANGELOG



## v0.13.0 (2024-05-22)

### Unknown

* Merge pull request #517 from FabienPennequin/feature/homeassistant_ws_batch_size

Send data to Home Assistant WS per batches ([`353c44f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/353c44f0f48798499a288562f494eb78d2014947))

* Merge pull request #512 from Rathorian/patch-1

Changing the link for the configuration file reference ([`de3ba6e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/de3ba6e29eb82c8009e50155f87f58f05d470c74))

* Merge pull request #510 from koukihai/koukihai/fix-tests

tests: fix tests + stop tracking logging file and line_no ([`5103919`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5103919531c3bbb40a086ae20f2ae82734e8446c))

* Simplify code ([`0bde36d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0bde36d05120f99f149ab1362759ea813f841031))

* Tweak logging ([`67cda56`](https://github.com/MyElectricalData/myelectricaldata_import/commit/67cda569969f73b35fb40301deef7205b9a0b1c1))

* Add batch_size param in config file ([`54a1a6c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/54a1a6c85aee671515bc1bf59c5c811c76a207b6))

* Send data to Home Assistant per batches

Avoid websocket timeout when data is too large ([`8173a52`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8173a526628fb40da25e801e7bfc66a1372d6b61))

* Changing the link for the configuration file reference ([`6863752`](https://github.com/MyElectricalData/myelectricaldata_import/commit/68637521d68ff1df6a39df8b4e5160dc7e18af59))

* more coverage ([`5e118e7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e118e76f93241c4bce474b0b46a34a0406d89a4))

* use pytest module ([`d64ee7f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d64ee7f5395a5ee48de296131789cff5a647ba7f))

* tests: fix tests + stop tracking logging file and line_no ([`e28a575`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e28a575517454ae0c5bff5f3705c0901f9fdb4ef))


## v0.13.0-rc.4 (2024-02-29)

### Fix

* fix: mqtt connect ([`4d3e919`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4d3e919c0d088f9a4b64d5990cc3c2448cc7cf03))

### Unknown

* Merge pull request #509 from MyElectricalData/fix/ha_sensor_rework_ha

fix: mqtt connect ([`5845a77`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5845a77bd93f774aec5f7316a3f9c7df86150a46))


## v0.13.0-rc.3 (2024-02-29)

### Fix

* fix: clean log + code ([`6459130`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6459130e27b0ea66bd56396ca542c49e35b3e82c))

* fix: makefile setenv ([`8f77775`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8f777756e7c3fe9f57d17753cef5374d578fb97d))

### Unknown

* Merge pull request #508 from MyElectricalData/fix/ha_sensor_rework_ha

Fix/ha sensor rework ha ([`3856bc8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3856bc830a52380673b6837e112f4ff239588445))

* clean: code ([`3c43625`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3c43625f8d6ccfa649dc0717c59e86bc73118146))


## v0.13.0-rc.2 (2024-02-29)

### Chore

* chore: clean code ([`1680068`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1680068d62a5480dcb631edb027a993fba2faccc))

* chore: clean + doc ([`5139e5d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5139e5d78da9e8b1c9f2fb90af3a36184cde1f31))

### Ci

* ci: update ([`a484cf6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a484cf61639fc823ceb1f267e8b3cda384792937))

### Fix

* fix: rework class ([`9fc4468`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9fc4468851ccba8f91f7664767cdb28110751192))

* fix: fix sensor class ([`c1ffbc5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c1ffbc5d819ceb029cc08843a397f9157beb8337))

### Unknown

* Merge pull request #506 from MyElectricalData/fix/ha_sensor_rework_ha

Fix/ha sensor rework ha ([`f2b9811`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f2b9811b92ab13e88c4d2aca68a0185374f42ad0))


## v0.13.0-rc.1 (2024-02-26)

### Feature

* feat: add sensor create in energy dasboard + fix: HP/HD ([`5ed9171`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5ed9171ef952737e46a6a7f8a0c2e4c9aac764cc))

### Fix

* fix: https://github.com/MyElectricalData/myelectricaldata_import/issues/491 ([`6b19700`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b19700306e0b608f026459ba258722cf3751617))

* fix: isort ([`9dc054c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9dc054c9d6544888148c1580ef7ad105ec974a41))

* fix: divers ([`bfc149a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bfc149a791990e539fc758de44c76b67dc2a7be7))

* fix: update python lib ([`962112f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/962112f97e3b63543e200ea346f78b7da132f2e3))

* fix: remove tempo from exemple ([`e43676f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e43676f90b5050d565240d16392a2dcdf196a8b4))

* fix: fix type in config.yaml when change config ([`17ae37f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/17ae37f8c33efe3ea2eaa5c52efe6e53fa907fdd))

* fix: create ha sensor create by home_assistant_ws ([`7380db0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7380db0c917fc5d34c85546174ecfc7fc9702bf3))

### Unknown

* Merge pull request #503 from MyElectricalData/fix/isort_491

Fix/isort 491 ([`fcae211`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fcae211116134fa9375b16a0561ab47f835f26e2))

* Merge pull request #502 from MyElectricalData/feat/ha_sensor_from_energy

Feat/ha sensor from energy ([`0d431a3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0d431a3e50881bb6559e17f0d56aa398c081b989))

* dev: add dev standart ([`d57f9ff`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d57f9ff7590714d8e4a933db60119258607cd021))

* Merge pull request #500 from MyElectricalData/feat/devcontainer

type: change image ([`41fadc9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/41fadc9bec6663e2ec66003c86d380b3f739a60c))

* type: change image ([`c38e73c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c38e73cb74828ef9da6d059921c21cb72e827ab1))


## v0.12.0 (2024-02-19)


## v0.12.0-rc.1 (2024-02-19)

### Chore

* chore: add devcontainer ([`f5dd2a4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f5dd2a45305d9c171e4ae574334bda6d6a7934ff))

* chore: upgrade to python 3.12.2 ([`bffe1c2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bffe1c2686e6e81c747d940da6895e8f7115ef65))

* chore: devcontainer ([`70e4aca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/70e4aca04db856afc8c8e6bc9507847cb55f7b52))

### Ci

* ci: add devcontainer ([`7664475`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7664475aa0344f4838de789059af82b761bbf616))

### Fix

* fix: devcontaienr post-install ([`211371e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/211371ea8a06e0c1a8e9ba1d6fa38c187bf9be75))

* fix: send tempo sensor to HA always ([`91456c9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91456c9c998223b4a9ab816881f72dcedde22f03))

* fix: python version ([`5710106`](https://github.com/MyElectricalData/myelectricaldata_import/commit/57101067400d4f3b6b5827fbd2937f5b1425ef86))

* fix: test ([`d0ca933`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d0ca93302f77529f21e575f6c81e5d3a28f0c887))

* fix: test ([`79c0981`](https://github.com/MyElectricalData/myelectricaldata_import/commit/79c098108d4fbe1be487a200259c932e3f40db13))

* fix: test ([`0374f0b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0374f0b889ecdfd39a7c52f6cf181930daf8a86f))

* fix: test ([`e734cac`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e734cac88d17c2f378ea48423ec28861cc531d61))

### Unknown

* Merge pull request #498 from MyElectricalData/feat/devcontainer

Feat/devcontainer ([`f4b241e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f4b241e8afce2269f81512f47647ef977ed9aff8))

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import into feat/devcontainer ([`3172f45`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3172f453ed16846721692c38ea86b97ba5752b41))

* chore upgrade lib ([`0826eb2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0826eb2f84d455333145799fd57b12b6ce04c3c4))

* dev: release devcontainer ([`e75acdf`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e75acdfab308143bc7e194327a52d35b9a04266e))

* clean: devcontainer ([`988ad9a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/988ad9a7b023ab94ba54f3f0f1204084779e8d5a))

* Merge pull request #496 from MyElectricalData/feat/ha-production

Feat/ha production ([`ed0ba55`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ed0ba55d1f0104a06702a56140b52ac826286211))


## v0.11.0 (2024-02-15)

### Feature

* feat: add production in home assistant energy ([`9c3aa3c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9c3aa3c7e80818676972e2ac993bdd02957821e0))

### Fix

* fix: production daily html + doc ([`96598e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/96598e61e14570dc0faeafed28983688b945edfb))

### Unknown

* doc: add purge ha ws to config example ([`4851a1a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4851a1a73b0787b7883e88e7c379d60d64b8704a))


## v0.11.0-rc.3 (2024-02-12)

### Fix

* fix: display bug if not tempo ([`a36f18b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a36f18befc6ccd4521cc7a19b1e5c9195e443ed6))

* fix: https://github.com/MyElectricalData/myelectricaldata_import/issues/494 ([`6af83f1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6af83f167e53754d82dfb48f32ce37c42b3703ef))

* fix: https://github.com/MyElectricalData/myelectricaldata_import/issues/489 ([`c484d4b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c484d4bf14d38c26fbcacd0cbce9dcbe1a3afcfc))

### Unknown

* Merge pull request #495 from MyElectricalData/fix/494-489

Fix/494 489 ([`ca35bff`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ca35bff3049e903f49e27678ede9c7c315871f1b))


## v0.11.0-rc.2 (2024-02-10)

### Fix

* fix: https://github.com/MyElectricalData/myelectricaldata_import/issues/479 ([`7609cdd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7609cddc53862826454e3c1bf7c04a67aab7d135))

### Unknown

* Merge pull request #490 from MyElectricalData/fix/issues/479

fix: https://github.com/MyElectricalData/myelectricaldata_import/issu… ([`02444a7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/02444a75809afed2020f3c57f4d539f94109aa70))


## v0.11.0-rc.1 (2024-02-06)

### Feature

* feat: add max_date to Home Assistant WS import ([`b4641af`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b4641afbf3f534adf8ddcbe2545fe0b12b12c928))

### Unknown

* Merge pull request #488 from MyElectricalData/feat/issues/445

feat: add max_date to Home Assistant WS import ([`dec5d4e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dec5d4ed9034450fc2f7cc7d811344db5b2e9ecc))


## v0.10.1-rc.2 (2024-02-05)

### Fix

* fix: add install-github ([`7276830`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7276830bd71103362af87ff4d485e3a5e60c9661))

### Unknown

* Merge pull request #487 from MyElectricalData/fix/tempo_days

fix: add install-github ([`23ac718`](https://github.com/MyElectricalData/myelectricaldata_import/commit/23ac718143a088f1df453fb00c0c2a930aefc9f6))


## v0.10.1-rc.1 (2024-02-05)

### Ci

* ci: clean ([`ca54fa6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ca54fa6ae2c51c4ad8acf6b11d3b11e0d1843449))

* ci: fix ([`48a4aed`](https://github.com/MyElectricalData/myelectricaldata_import/commit/48a4aed734f43e1a57112f225ad7c5f9d0e244f3))

* ci: clean workflow ([`40b51e3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/40b51e39f1a177a6b14bab0114512a22e54c58e5))

* ci: test ([`3661dff`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3661dff643ce1d042f8e8a96545399d3b5be4892))

* ci: test ([`1106e25`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1106e25b45ebb4bd0e48e54e2cea4fe166eca58b))

* ci: test ([`5d64ddc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5d64ddc5ab17d0ba19b93788047af42599a5a140))

* ci: test ([`91a5df6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91a5df649908e5d3e9b572a1bb49b256f9ce20b2))

* ci: test ([`9460710`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9460710cc45816b1b30492c013584fa0bb0a4a60))

* ci: test ([`0bf182a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0bf182a35fc39e4de8d0c2bb7ebdc6d808f55a2a))

* ci: test ([`99ae339`](https://github.com/MyElectricalData/myelectricaldata_import/commit/99ae3394e6cdbe4e574685526186ad73d90357c1))

### Fix

* fix: tempo days color ([`bdee3e1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bdee3e1796f3cadeea4dd998cce9433e6955b63a))

### Unknown

* Merge pull request #486 from MyElectricalData/fix/tempo_days

Fix/tempo days ([`2ed1ca6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2ed1ca6668e893116e881e84867cefde332280c6))

* Merge pull request #484 from MyElectricalData/ci/test

ci: test ([`a2562d7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a2562d78e406ae1d216fa00f66f0b92e4a260fc3))

* Merge pull request #483 from MyElectricalData/ci/test

ci: test ([`f64dc29`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f64dc293e42292cc56f0583906e237524a03cef8))


## v0.10.0 (2024-02-05)

### Feature

* feat: release 0.10.0 ([`69efe32`](https://github.com/MyElectricalData/myelectricaldata_import/commit/69efe3279d5bbffd7ddb4567ab25ee1f7b773b96))


## v0.9.0 (2024-02-05)

### Feature

* feat: increment release ([`9830cbd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9830cbde8f80e9ac83d5b62ec9e87b9a076fe4e2))


## v0.8.0 (2024-02-05)

### Feature

* feat: increment release ([`274fa9a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/274fa9afed9f62b17cf61590e030ea3658c31089))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`39bdd95`](https://github.com/MyElectricalData/myelectricaldata_import/commit/39bdd959c04fdcaca3b23548487f59d75fda2916))


## v0.7.0 (2024-02-05)

### Feature

* feat: increment release ([`7e289b1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7e289b129dbacf453e95e69605ec49d88cc25e99))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`e0c62f4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e0c62f432dccfab1c2370bd35770180e6c68732e))


## v0.6.0 (2024-02-05)

### Feature

* feat: increment release ([`95cc8b8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/95cc8b8c49d238421279cdddd589db64df175286))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`2a8b5fd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2a8b5fdce8977f51707c55f9997a83d8f86e69ff))


## v0.5.0 (2024-02-05)

### Feature

* feat: increment release ([`2beee75`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2beee75d4f17c7d0f6d1ddb305df5b7f44be65da))

* feat: increment release ([`85c13b2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/85c13b2649034a924b313d695ec7d415f56cb71f))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`8ab69ab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8ab69abd894641bab616f931302a51176177468d))


## v0.4.0 (2024-02-05)

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`e7f35a7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e7f35a7d80482514a40ff7bd1807057959924292))


## v0.3.0-rc.1 (2024-02-05)

### Feature

* feat: increment release ([`f66aa7c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f66aa7cd918ee8822820b0572f5f33982f096a71))

* feat: increment release ([`1f7b318`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1f7b318c38d894ccf9c8ad1301cd97007a503122))


## v0.3.0 (2024-02-04)

### Feature

* feat: increment release ([`f46a2d9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f46a2d91e108698ff0e2d79ad5b207c14bbdd1ff))

* feat: increment release ([`1214c11`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1214c1137c141d5c62ebd565b209b802b8daaf94))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`45fc428`](https://github.com/MyElectricalData/myelectricaldata_import/commit/45fc42849791ef422a591fa0540e6a7fe23ed00d))


## v0.2.0 (2024-02-05)

### Feature

* feat: increment ([`6b12e4d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b12e4da878bd7c1d3fb9f4c58ba6f1ab8aae434))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`3780e26`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3780e26bc2bbe615321398410c592fb2e4a56e63))


## v0.1.0 (2024-02-05)


## v0.9.3-rc.2 (2024-02-05)

### Fix

* fix: regenerate version ([`273d743`](https://github.com/MyElectricalData/myelectricaldata_import/commit/273d7435d309c1954e3c8f3be49c4972a7a0dd2d))


## v0.9.3-rc.1 (2024-02-05)


## v0.10.0-rc.25 (2024-02-05)

### Fix

* fix: clean ([`f39bebe`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f39bebe9c0f8254baa9a12994d661ad6eb162ca5))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`963755a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/963755afd78b53c2a9d3ea1daa63e85be3547bee))


## v0.10.0-rc.24 (2024-02-04)

### Fix

* fix: migrate to sem input ([`2c5999f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2c5999f62054914f5a96b0ec21008d24dabb5073))


## v0.10.0-rc.23 (2024-02-04)

### Chore

* chore: clean ([`5e1c2dd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e1c2dda28a8471a395134cb0bd10f7e8750d862))

### Ci

* ci: run ci only on PR to main ([`2dfb992`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2dfb99216a7120a14af9b10cdfbcdb25cdef3938))

### Fix

* fix: generate rc ([`697834c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/697834c6693e5366dfa72abdbe02fc05c9ad1cd1))

### Unknown

* Clean ([`8fc7819`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8fc7819bf438f5b080ce2c86efb0c68ec25ad3e7))

* Merge pull request #482 from MyElectricalData/vingerha-main

chore: clean ([`211c2db`](https://github.com/MyElectricalData/myelectricaldata_import/commit/211c2db1e6e4e57dd6c9a29b242507b5d35b2a63))

* Merge pull request #481 from vingerha/main

Fix: get_week ([`988b9a6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/988b9a69ea7518e0a264cce6a1621bae1ee99442))

* Fix: typo in get_week

now instead of now() ([`6c96e78`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6c96e784c958b9ea334be0ec99f17f0fccacf141))

* Merge branch &#39;main&#39; of https://github.com/vingerha/myelectricaldata ([`0bfaa5e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0bfaa5e6f7120236798337e6cb3c8a092377fce7))

* Fix get_week

Base on &#39;today&#39; and adapt for leap-year situation ([`55b4e6e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/55b4e6ee1d59742d9522411088d0d739187b29c1))


## v0.10.0-rc.22 (2024-01-30)

### Feature

* feat: add hp/hp &amp; tempo to daily comsuption ([`6d0c4b7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6d0c4b715e15127caa38171f2217fde906e6da4c))

### Fix

* fix: loading hide ([`a9035b6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a9035b61b7834a5b590c94e4848b61c32ab72095))

### Unknown

* Merge pull request #475 from MyElectricalData/feat/hp-hp-tempo-daily

Feat/hp hp tempo daily ([`0ae2ff0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0ae2ff0c78edbe6ad88717aae45167659b529850))

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`d4439c6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d4439c62de890e787b63e7c3cb39781e2b4b91d7))


## v0.10.0-rc.21 (2024-01-29)

### Fix

* fix: imports conftest ([`9ceab7d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9ceab7d35eb51017c342685d027a9e573d1082d0))

* fix: tempo data in usage_point ([`27df24c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/27df24c032fc0d182514c5ad89131325b154008e))

### Test

* test: add github action ([`a7b1900`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a7b19000591a4b19fe3af5e7fd97c02e5d151850))

### Unknown

* Merge pull request #474 from koukihai/koukihai/mock-requests

tests: Mock requests et DB ([`94adc88`](https://github.com/MyElectricalData/myelectricaldata_import/commit/94adc884a8ed3a3958daf7a9ee43d7728d748c10))

* move comment ([`e2736fe`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e2736fe5a708f1b47531ef5e00106e7a3758c086))

* Merge remote-tracking branch &#39;upstream/main&#39; into koukihai/mock-requests ([`5cbb69e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5cbb69ee716a36014e4eaa8ef2e8dd78c0894493))

* mock: /valid_access/{usage_point_id}/cache ([`803de87`](https://github.com/MyElectricalData/myelectricaldata_import/commit/803de879fe29bf9b99a8557d0725500c81e73ada))

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`f1314a2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f1314a221ac6cc111e8d59321e73a1f6f1c120c3))


## v0.10.0-rc.20 (2024-01-29)

### Ci

* ci: update ([`719169c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/719169c77723d21cf908ed059b32edd330c7aa7e))

### Fix

* fix: add dev mode ([`7becf9e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7becf9ec6939cbd25245bbacd72ae45822d039de))

* fix: support DEV/DEBUG update ([`00bd332`](https://github.com/MyElectricalData/myelectricaldata_import/commit/00bd332b78ebefd8e7b1b712bd3e65af7de03c5b))

### Unknown

* Merge pull request #473 from vingerha/main

Replacing &#39;year&#39;-number with &#39;current&#39; in case it is current year ([`b3bda75`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b3bda75fa3e33febe32fd5468acac4abc34715bb))

* Replaying &#39;year&#39;-number with &#39;current&#39; in case it is current year

Allows to call MQTT topics having data for current tear directly from HA sensor (and others) ([`4fd6afa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4fd6afa7f187baeb3592e066b431975aa174be2e))

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`810742c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/810742c7300615f4d7851b6a2d3c09c41bb802ac))


## v0.10.0-rc.19 (2024-01-27)

### Ci

* ci: test ([`963095e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/963095e9af91d34df6e1dced26ac8d2af67d30d0))

* ci: test ([`d468100`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d468100c445e5e815d86c16e287712e07c5074d3))

* ci: test ([`5024826`](https://github.com/MyElectricalData/myelectricaldata_import/commit/50248260ddad3626d148d9352095863210659a8a))

* ci: test ([`8bfefc3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8bfefc3499d8032bfd31f12893a5d18905623f97))

* ci: test ([`78250d8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/78250d87b5a6191a30a312e84123bd71eee1ba8f))

* ci: test ([`a9f4c6c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a9f4c6cb1b9c05d05648658283352f82422c9f30))

* ci: test ([`337df7d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/337df7d0d1e6fe441f58adb832800cf33403dbbc))

* ci: test ([`704ad6c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/704ad6ca07fd45cf436eaf2cdfdb4cf6651d8526))

* ci: test ([`d5b2276`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d5b22763f5022e8618b3530f3ac4127befabd7d5))

* ci: test ([`7684b09`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7684b092e058c6d945cbef10f9a2855ccb086b4e))

* ci: test ([`8ab3f15`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8ab3f15855a70563dce936c9acc043c64abd1328))

* ci: test ([`b587f83`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b587f83e98e6abc3f89e79d34fea1c045d1c3e2c))

* ci: test ([`81c3a18`](https://github.com/MyElectricalData/myelectricaldata_import/commit/81c3a1886e2350f99486b239d98bfeb33e639e3a))

* ci: test ([`3e312d1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3e312d1499fbe791f2ca0df8f69d7d280c8e2f64))

### Fix

* fix: remove pytest.ini (configuration in pyproject.toml) ([`55a9929`](https://github.com/MyElectricalData/myelectricaldata_import/commit/55a99291c8ebee722b1bebbaaf9c314ad6be33de))

* fix: update lib ([`ae9ace4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae9ace4f51c905e618c625e1e7a6aefdd8de1dee))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`1c234a1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1c234a13b2a31384aea3d28beae1c674f4ba75c2))

* Merge pull request #469 from koukihai/to-upstream/fix-tests

fix: tests ([`602e2f1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/602e2f131538679a9afe80eb97634b82fb4e224f))

* Merge branch &#39;main&#39; into to-upstream/fix-tests ([`5482eab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5482eaba6b4062ddf1662b7bbca609e6ab729069))

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`c335f51`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c335f5116bb66813e7826cb06a0d9d255bb173f6))


## v0.10.0-rc.18 (2024-01-26)

### Fix

* fix: ci secret ([`690f8ca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/690f8cae29919a470490f69f990ac0389ee2d09b))

### Unknown

* Merge branch &#39;main&#39; of github.com:MyElectricalData/myelectricaldata_import ([`6821339`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6821339cc41c22fcc3af664ce4819e82bd80dd5e))


## v0.10.0-rc.17 (2024-01-26)

### Chore

* chore: test ([`3bbeacc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3bbeacced3cb697aff0d66d75c1dba0ce9697e11))

* chore: test ([`9ea527e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9ea527e22799ea5ca4dbd041c9182f1e284693de))

* chore: rename ([`ddbd8ce`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ddbd8ce1bd9ea2a3a0ba77cf296c9815efcbb6c8))

### Fix

* fix: rework ([`2c977d0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2c977d039db928e24a0f1ecbaeea026b2638a437))

* fix: fix ([`8876423`](https://github.com/MyElectricalData/myelectricaldata_import/commit/88764230e4cd3d9e117954d6f03d3e689099db96))

* fix: move .github ([`8ed6a1a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8ed6a1aa39dca8f25e2f7eab3e2d9066565df327))

* fix: move to .github ([`1ec1838`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1ec1838c76f82bfa877321d0df95e8d8a2970272))

* fix: test ([`2711d09`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2711d09f9ebee2d0833d3e4e3764e4492f81eed6))

* fix: test ([`4f51752`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4f517523d8e9b94cf3948c86b26d491e01787b55))

* fix: test ([`27b9e8b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/27b9e8b1d36e58ef9f7c7bb7d3c943c675c3090f))

* fix: test ([`1d34f10`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1d34f105ab55ddb2cf38ce168dab9039e08e8f12))

* fix: test ([`a918b9e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a918b9ef878e2ac8463c89977a5315115dfe7f04))

* fix: test ([`b786759`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b786759f22816935df5b9d4cb2ee3c4dbc23c98b))

* fix: release ([`27b08c7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/27b08c7c27baea6340c79ca5e9779f9aaf25510e))

* fix: use external workflow ([`ebe074c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ebe074ca99eb649df96ee6d51ba3391e7964f141))

* fix: tests ([`b82e817`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b82e817bbd5825978a2aa79e9015ed975e660bdf))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`4d66a52`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4d66a52c0a79897b23af38b52f864c44ee821fdb))


## v0.10.0-rc.16 (2024-01-23)

### Fix

* fix: condition ([`b15e73a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b15e73aea6804cbf0af3a62c28b6b8dda902f1ad))

### Unknown

* Merge pull request #466 from MyElectricalData/koukihai-to-upstream/443

Koukihai to upstream/443 ([`368537e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/368537ec256e87a1cc8babaf9e22fd8c1f6bd7d0))

* Merge branch &#39;main&#39; into koukihai-to-upstream/443 ([`c38baa6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c38baa667a2e3aac4c4462ff7bb14d9857b1f7a0))

* Merge branch &#39;to-upstream/443&#39; of github.com:koukihai/myelectricaldata_import into koukihai-to-upstream/443 ([`46bb802`](https://github.com/MyElectricalData/myelectricaldata_import/commit/46bb802dc7a58a98e1614b5ceeb640a2b29e0bd4))


## v0.10.0-rc.15 (2024-01-22)

### Fix

* fix: needs ([`3a56a82`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3a56a82440efa63329052a5024f98f6f02c77561))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`1bd7224`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1bd72242940c17476fd4cc46c5d1f6d0fe0fe339))


## v0.10.0-rc.14 (2024-01-22)

### Fix

* fix: build arch ([`94a47c3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/94a47c36710954d42d87732f112456aecc87a75e))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`2634fe2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2634fe2fec5f07dfe90431d8248a9219924f96ba))


## v0.10.0-rc.13 (2024-01-22)

### Fix

* fix: cd ([`4e2dc94`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4e2dc94211be5d259a711e72a509062660b41493))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`4942aab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4942aab4bb578615a96a1f6a1f3533d7c9a8c459))


## v0.10.0-rc.12 (2024-01-22)

### Fix

* fix: cd ([`469bf46`](https://github.com/MyElectricalData/myelectricaldata_import/commit/469bf46aae56685d658d1c1921b7d0e16b38becc))


## v0.10.0-rc.11 (2024-01-22)

### Fix

* fix: yaml cd ([`ff2e669`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ff2e669269f885bb71b5f4d86ef1b8a377209dfb))

* fix: yaml format ([`46da4b4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/46da4b49479ee0de6a5d68b67af778759488d28b))


## v0.10.0-rc.10 (2024-01-22)

### Fix

* fix: cd yaml ([`f1857d6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f1857d6d353c7e4f39f77b900aa76f67a0764d8e))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`1d98b6b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1d98b6b4c4b790825abc3fab702627b90e6a3a4e))


## v0.10.0-rc.9 (2024-01-22)

### Fix

* fix: yaml format ([`56fee28`](https://github.com/MyElectricalData/myelectricaldata_import/commit/56fee28df353632632066fcfac15e45536e7db7c))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`b434e2e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b434e2e0516da067c736ec036297be9e786cce1f))


## v0.10.0-rc.8 (2024-01-22)

### Fix

* fix: dispath docker arch ([`47e0941`](https://github.com/MyElectricalData/myelectricaldata_import/commit/47e0941239b172ce6fec13f4d6f8445b758a8299))


## v0.10.0-rc.7 (2024-01-22)

### Fix

* fix: remove pip-compile ([`6049475`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6049475acf67b9c4f7fcc5b659a2fb8c22bef79a))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`51ee6c9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/51ee6c9ae2a91b7d3c1251efd4e87c8658a3badc))


## v0.10.0-rc.6 (2024-01-22)

### Fix

* fix: outpit indentation ([`54a818b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/54a818b6afa5c406861c5636b2b32fdd0868570a))

* fix: regenerate version to debug ([`97ee434`](https://github.com/MyElectricalData/myelectricaldata_import/commit/97ee434c1b89de0ab723f13a34bfbcb2071405e8))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`eba1f8f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/eba1f8ffb386fa1be03e29c93ae8fe022c95d9fc))


## v0.10.0-rc.5 (2024-01-22)

### Fix

* fix: vars prefix ([`467f8bd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/467f8bd65c49e807d9f5de2cbd7dd2f52a171b40))

* fix: deploy version vars ([`844d1ca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/844d1ca6a8adaad552ff1ac4a0c23871fa3a4ef9))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`c9f334c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c9f334c192e79adc647e829018b5627a68707a02))


## v0.10.0-rc.4 (2024-01-22)

### Fix

* fix: deploy cd ([`53d783b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/53d783b4cf911e9e993cb974ecfc31afb82d6f82))

* fix: output ([`fb2aaad`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fb2aaada3deeff5dd6447fba649d5e93bddc3018))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`84f4a52`](https://github.com/MyElectricalData/myelectricaldata_import/commit/84f4a52b58ef097a8603a4c6af420e7024d3003b))


## v0.10.0-rc.3 (2024-01-22)

### Fix

* fix: runs-on worker ([`7a1800b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7a1800b7e5b4b066c3684629072851a56b6a7d18))


## v0.10.0-rc.2 (2024-01-22)

### Fix

* fix: rework deploy ([`186776c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/186776cad98ceb0ac4f57b3c0f26f5b2b6532dc2))

### Unknown

* Merge remote-tracking branch &#39;refs/remotes/origin/main&#39; ([`7e65460`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7e654605b11bfdae341014ce126a9a453e775bca))


## v0.10.0-rc.1 (2024-01-22)

### Feature

* feat: add semantic release ([`5615745`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5615745c67a8b951b61627d93cef9db8b0360730))

* feat: rework poetry &amp; co ([`ea39f44`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea39f4466f2d8ab84d19394b605e78856981fe8c))

* feat: connect to mqtt via ssl using certificate authority (ie. no host validation) ([`bb2a6da`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bb2a6dacbc7011f8c6f75090475e697032c442ea))

* feat: update ([`fb657f9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fb657f923586fb8625419ca35aecb30c836a52c6))

* feat: add storage_uri with postgres compatibility, rework database access ([`de37b8c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/de37b8c3e5537801770ebf5cefe210aececd7983))

* feat: fix #342, #341 ([`86974f3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/86974f3d82e8633f94d58cf16a73f90d44641610))

* feat: clean ci ([`50e1045`](https://github.com/MyElectricalData/myelectricaldata_import/commit/50e1045ce332150a0a7bf72febceb78bd2db4722))

* feat: clean ci ([`3890719`](https://github.com/MyElectricalData/myelectricaldata_import/commit/38907193521ac5b9346f36d6fc419cd19043ae99))

* feat: add pr #319 ([`6c70110`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6c701103cc7b17c518621ac50bcb57925424fd5b))

* feat: clean ci ([`597a6ef`](https://github.com/MyElectricalData/myelectricaldata_import/commit/597a6ef89ea6ac80f53c5c91d4b122669b574c18))

* feat: fix #323 ([`fbdd794`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fbdd794095a1cc94c4c0f35f9846964ca8e8d9b1))

* feat: ecowatt + tempo ([`ef4b4b0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ef4b4b0b21e6d6cb86eed0b167da7382dbba4790))

### Fix

* fix: semantic release path ([`d7320d1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d7320d1cedb78f679fec55b64fde9211a9f65760))

* fix: semantic release ([`df63a45`](https://github.com/MyElectricalData/myelectricaldata_import/commit/df63a45ac335ad18766bc833f06191a1055b1e25))

* fix: populate production details ([`d01bcad`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d01bcad87263dcb6f3232c6857cabd1bc03522bf))

* fix: handle inconsistent consumption/production ([`b1302ab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b1302ab07b2ade2965ff587e2572c42406158636))

* fix: url issues github ([`80f050f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/80f050ff078a21f9d7fcb085b015ed13150e45df))

* fix: tempo ([`09f2c4d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/09f2c4db131aa1b9055d33928df8560ebfe71515))

* fix: https://github.com/MyElectricalData/myelectricaldata/issues/399 ([`edc0bd0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/edc0bd070afc2a2d7bb013352333cef4a560a0a3))

* fix: test psycopg2 ([`9686fd8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9686fd80c0eab18ccd2c085203a091bc24e366e3))

* fix: test for psycopg2 ([`cf1b6e4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cf1b6e42b70462ace0471e03d4fe60a44e99d10f))

* fix: upgrade to python:3.11 ([`52c125f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/52c125f217d550c676bc6b6ee6f93a1f9b6cf0c1))

* fix: switch python lib psycopg2-binary to psycopg2 ([`d73ad5d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d73ad5dc18a3c79515f0f85e7bdeaa620966958b))

### Unknown

* Merge pull request #452 from MyElectricalData/0.9.4

0.9.4 ([`f642c70`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f642c7034e3dd09d93f9eab6be5434ea1728a1f2))

* merge: mqtt ([`dba4d62`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dba4d62933da77e98bbc1844abc006793bed0bb3))

* Merge pull request #461 from koukihai/to-upstream/454

feat: connect to mqtt via ssl using certificate authority (ie. no host validation) ([`de7826e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/de7826e0ba03c038ac1bacc44c2b9183b846b8d2))

* Merge pull request #455 from koukihai/to-upstream/unittests

Unittests for jobs.py ([`0010b81`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0010b815e218facc770763c5f133782a654cb40c))

* Merge pull request #456 from Rathorian/master

fix: url issues github ([`b9c25d1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b9c25d15840625594eb0df640edeab9bd55f5b12))

* add test_usage_point ([`ab1b353`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ab1b35369910b9dd5483b9bb747f1ab8afc284af))

* Unittests for jobs.py ([`2590a8d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2590a8d4855bfd6afd90415b6d563e9846b76b25))

* fix sql error ([`9988a66`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9988a6663dfc47d28fdfa57ac05193f3f569a5d6))

* fix regression ([`c33b559`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c33b5597ac75f5e8d2a01a5ba2b86fe9ccd50f05))

* clean ([`dfa61c2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dfa61c254b91ccb8e06ef87bb7a7e957eb05b894))

* Merge branch &#39;0.9.4&#39; of github.com:MyElectricalData/myelectricaldata_import into 0.9.4 ([`f90c587`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f90c587e0b38d57715e8158f3ddb25816167a5c9))

* Merge pull request #451 from MyElectricalData/revert-449-only-unittests

Revert &#34;Ajout tests unitaires&#34; ([`662afe4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/662afe49cc0b5bf5d924a0ce509559581b530f05))

* Revert &#34;Ajout tests unitaires&#34; ([`3733208`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3733208efca449436393fe62853aa236a206dafa))

* clean ([`fbeb3ac`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fbeb3acda2e9c753ea2dc3e3bff081e9391278e2))

* recommit ([`08463e4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/08463e4a7973bfb1a8177630c12876536234876b))

* Merge pull request #449 from koukihai/only-unittests

Ajout tests unitaires ([`e418f8b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e418f8bfe8f316ff5cbeface483108d29cd06d2d))

* 0.9.4 ([`477b7e5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/477b7e5de9fc0947cc8a8d01272608744fd935ea))

* remove unnecessary import ([`5e48a61`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e48a61d48d9b263043f4851389fdd291af5feb0))

* add doc ([`49c631b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/49c631b722fe179b381e596162197e99127508e2))

* bootstrap unittests ([`19bca3d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/19bca3d0952ba8460ec3be8aa9b09feb98a10a3e))

* 0.9.4 ([`e1abda8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e1abda82df527b620fb677f64520db37bfbe20c9))

* Merge pull request #428 from MyElectricalData/0.9.3

fix: tempo ([`35ded9a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/35ded9a7aece1958dd8a3569177ea94d93ac6cd3))

* Merge pull request #398 from MyElectricalData/0.9.2

0.9.2 ([`4a446f2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4a446f2aa1a39cbcee059f87bc488f5e84046c74))

* fix mqtt name ([`5f27fc7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5f27fc783ba7c4cb9ea8237d3f2d51d33ac27938))

* Fix unique_id ([`7990cab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7990cabffd4704241d46e0d1f7605fa126335956))

* maj doc + fix ([`9110228`](https://github.com/MyElectricalData/myelectricaldata_import/commit/911022892945071cfbb9e8174aeabd35607225d4))

* add ha ws enable ([`e53f784`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e53f784a6b0988d32aba5b0a0a98b91284e7697c))

* Home Assistant WS ([`a3ca4b9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a3ca4b9295094de9281ed8dfdecf01d630f16792))

* Update version ([`04f1396`](https://github.com/MyElectricalData/myelectricaldata_import/commit/04f1396816fb8afa152fe37a4fbfc951e294cc6a))

* maj ([`04077ac`](https://github.com/MyElectricalData/myelectricaldata_import/commit/04077ac66dead8b1c0cbf8910563e86575527799))

* Fix value of kwh ([`f338f09`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f338f094a08facc8a961bf20b373cb93212e15a9))

* Fix EUR/kWh + add tempo info ([`520c377`](https://github.com/MyElectricalData/myelectricaldata_import/commit/520c377c71a41991dae5a98819b84e8890b8a37f))

* Add sensor HA ([`04667be`](https://github.com/MyElectricalData/myelectricaldata_import/commit/04667be3510f9c5811b3f9cfcbd5903ab3092d8d))

* Add errorLastCall ([`651c6d5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/651c6d5748322bf4df3c763ee2319b14e349b58a))

* Fix https://github.com/MyElectricalData/myelectricaldata/issues/400 ([`77a323d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/77a323d53e3f1cc96bd19b2d86ce3df19b48be8d))

* Merge branch &#39;0.9.2&#39; of github.com:MyElectricalData/myelectricaldata into 0.9.2 ([`899d80c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/899d80cfbdee1d2a2c2aa4c59a501ec365692b84))

* feat : if data in tempo stat ([`952a396`](https://github.com/MyElectricalData/myelectricaldata_import/commit/952a396c1e670805f2f1e62aeb12e5370639688f))

* Merge pull request #402 from vingerha/0.9.2

Various ([`f407ddd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f407ddd8fa315bcf74372caa048c045cc6d9f0c0))

* Fix state for Ecowatt sensor

show overall state instead of 124356.0, this allows easier automation based on sensor value ([`be23428`](https://github.com/MyElectricalData/myelectricaldata_import/commit/be23428704f5dec5d003a869c62fd824a7c060ce))

* feat : fix var ecowatt ([`91502a8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91502a8c4be1abed501b004d686d839253c2a424))

* Merge pull request #381 from MyElectricalData/0.9.1

0.9.1 ([`2be320d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2be320d1fdcba8fc16741178295d385f38525b9e))

* feat : fix date ecowatt ([`a903f37`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a903f3707719b07ba4349641e0195e124747337a))

* Clean ([`3813103`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3813103ab4d0b1f168322aa5062811deb9433f07))

* Maj version ([`85b6937`](https://github.com/MyElectricalData/myelectricaldata_import/commit/85b69374f0966cdaa73ad40d4f67afdb61eb9c46))

* feat : clean + fix ratio hp/hc ([`3836ba2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3836ba2c0cb12c47e37d12719c9b5173c3d0a888))

* feat : ecowatt remove begin/end ([`4436f0c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4436f0ce2100034f9c89ffc893cb47c870efdf93))

* feat : add ecowatt j1/2/3 ([`c91b8cb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c91b8cb5b2880a60d9d235358602653e53b1ad45))

* Clean ([`6437f05`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6437f0567ef65dc014d90fa6ab6b3467abe7b0fe))

* Update swagger documentation ([`ccf7fbe`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ccf7fbe761503b7aa3f7a11e79483f025f1f5052))

* feat : fix cd ([`3acabca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3acabcadce1aaeff125bf24915ab6bc80bedfc85))

* Fix HC/Hp ([`9c9eaa8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9c9eaa8faaa62764b4dcef4922e50d0e68167c45))

* feat : merge ([`dce0c6b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dce0c6b2ffcc4c4941dcf4790e3f685efe7e3ffe))

* add device_class + yesterday_hp ([`0a68586`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0a68586e7d25ca60fb703f8a471fd327b2c72d04))

* Clean ([`75d978b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/75d978b0896b88efd0a8fcb3cff2e2b28386bd6b))

* Fix ([`8519a7e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8519a7e402049573f9e4fc652b5083925bbf7619))

* Clean ([`ffd4873`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ffd4873d99f41bc87c81140cbbdc2cdc0dc4201b))

* Clean ([`3d07c8b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3d07c8b014736e1992d13b7367e4a4a06753eac6))

* Fix MQTT Disable ([`8dcbc88`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8dcbc8865639090e528cdb8a668314187fa4fe71))

* Revert htmlencode ([`b582d29`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b582d293b8fbfd19f93276e71733cb82271ac943))

* Fix Influxdb ([`bde2b77`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bde2b771b33d81513dabba1f83c26e6b44151107))

* Clean HA export ([`fa1343c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fa1343c08f9c5ef24d8ec15ed36bd71efc51926f))

* Fix HA Sensor for ecowatt ([`d766f8e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d766f8e6dcae147222631541f5a41368b6097d32))

* Remove aiohttp ([`e5d966f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e5d966fe1417e7eda9cac22532b41bdf7a64921b))

* Fix &amp; clean ([`19ab7d2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/19ab7d20970a8171476736f98e3fa007c7ed2c61))

* Fix job + sensor unit ([`c7159d6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c7159d657ceb0187d7160e81065a4444c446fe57))

* Add tempo sensor to HA ([`b1ffb48`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b1ffb48602d934d83a5200901c91aa35bab43819))

* Fix ecowatt begin end ([`f6dca75`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f6dca754a07ec0ed952dde00a5f9e100729d268c))

* Rename MQTT ([`21d4b22`](https://github.com/MyElectricalData/myelectricaldata_import/commit/21d4b225bea5ddc061edd8c2331baeb4a429e2c5))

* feat : merge ([`36abfef`](https://github.com/MyElectricalData/myelectricaldata_import/commit/36abfefd5fed17b8839e6a65c5fba719413c7dad))

* Merge branch &#39;master&#39; of github.com:MyElectricalData/myelectricaldata into 0.9.1 ([`5790ff2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5790ff273332e75506b0375aa1502e7ae65556b5))

* feat : add port and ssl ([`280a5f7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/280a5f7ea00cad6d8c1a7134d5fc8974cf325d51))

* Fix CD ([`fc7f360`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fc7f360fc34d95e65810445dbf4093635d5baa1c))

* Merge pull request #365 from MyElectricalData/0.9.0

0.9.0 ([`4b4c9c4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4b4c9c401ba869f9462d59f2d4ab7bd991f8045f))

* feat : add english doc ([`d664f77`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d664f77f452a733843492708c2e7ec751cb3998c))

* Fix CD ([`e31cecc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e31cecc15c7c82d51305238e8577e7008a1d17c3))

* fix build fail on armv7 ([`6e44299`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6e4429921df8a69ab387bbad31d573e8ace15e99))

* Clean ([`ae64399`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae64399fe312f3032a1fe5d6c31be59e245d25ed))

* Fix tempo &amp; ecowatt ([`a2cd448`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a2cd448194957d4e9f3f9c8c4863f4f5fc9e54cf))

* Release ([`a58f60a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a58f60a29f466618bd72f37c2f7f96bc2b2f4238))

* Release ([`247aec0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/247aec0c50ef35ef69d83c415c76023bb853320c))

* fix datatable ([`7ee020b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7ee020b156442ed21277fb3fac81a3a58f230d24))

* beta4 ([`742cdb1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/742cdb1035643f1e61275430a6aa5f5c44540b39))

* Fix str2bool ([`a44fcae`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a44fcaebdd4e9c6d835936b2929c1270fbb193fd))

* switch to uncommited ([`668911e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/668911ea8136af36c0a43edb3118d54d71cd208b))

* Fix ([`87ade8f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/87ade8fd34e42ee3a69aa83e68494c023f7bba3e))

* Fix db config ([`f94db64`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f94db64d1006e2d0422e8a3763d8e4505c42a456))

* Init 0.9.0-beta3 + API + migrate to fastapi ([`87d6938`](https://github.com/MyElectricalData/myelectricaldata_import/commit/87d69388e143518143fe0ffd2a22280e6cd9bce9))

* Update FUNDING.yml ([`4153c78`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4153c7848dc85af5cf1f45f9f135f2d79450f69d))

* Merge branch &#39;0.9.0&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.9.0 ([`e6f577f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e6f577fe99b32442caaf580a2b5e7d339a01bf51))

* update release ([`2795043`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2795043f99ab837b5865746eb15e3cb35a87d0a0))

* update release ([`d352ffa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d352ffafb8d009b38191da77a83a39855a71a3de))

* fix : force database object refresh ([`1a55edd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1a55edd66d59ac2d12b07d811a7ae3b054d5e1e5))

* Merge branch &#39;master&#39; into 0.9.0 ([`9d35192`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9d351927a8fd15a44dfe91f3ff278ccac5d64140))

* maj release ([`7632e00`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7632e00f507b0b17e5befe824f8325470f205f2f))

* Merge pull request #363 from MyElectricalData/0.8.16

0.8.16 ([`6c39776`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6c397768993f7bf0c15a95e8825606c6156c2496))

* Update auto-close.yaml ([`37cdcf1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/37cdcf197b8d5957419b12da8e2852c41abac50a))

* Update auto-close.yaml ([`3722ce5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3722ce5205a32daf7a1ce846a2c3cb6e57de0def))

* Update auto-close.yaml ([`7804807`](https://github.com/MyElectricalData/myelectricaldata_import/commit/780480702d1f3ee2959129d94c9713e1bb37ca90))

* Update auto-close.yaml ([`06a1b92`](https://github.com/MyElectricalData/myelectricaldata_import/commit/06a1b929c3aaef274ae5ce17c6643862f2fe3b82))

* Update auto-close.yaml ([`ba50f96`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ba50f961b0ee0df9546a545e825529b28a5c1b29))

* Update besoin-d-aide--.md ([`d9a3c39`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d9a3c396e75fb3db167e591096409d102311ae4c))

* Update auto-close.yaml ([`f2d062d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f2d062d13c50cb7b169617c424ed8bd917ecacee))

* Update auto-close.yaml ([`79fdd35`](https://github.com/MyElectricalData/myelectricaldata_import/commit/79fdd35ffb92f83e33a45f05048d237c91591048))

* Update auto-close.yaml ([`9649e50`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9649e501c960a2a7e9f43b2fb916fd7b6075f14a))

* Update auto-close.yaml ([`9f69a51`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9f69a51e59c0a1883da16e663abba24179e7e1c3))

* Update auto-close.yaml ([`5889f38`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5889f3805ab130c1f803e3d7c4410db565301868))

* Update auto-close.yaml ([`32c69b8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/32c69b8b9e969a609e597c6c87467caa4be66cdc))

* Create auto-close.yaml ([`6e06bc8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6e06bc87dbea96047025ed9b09878a3ae78f39ec))

* Merge pull request #340 from MyElectricalData/0.8.15

feat: fix #323 ([`4557667`](https://github.com/MyElectricalData/myelectricaldata_import/commit/455766740e42f39244e4771b23b57d68b8311dbe))

* Merge branch &#39;master&#39; into 0.8.15 ([`e4359c6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e4359c6b65360a1682efe32d4dd1a15da785af26))

* maj rlease ([`92152d5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/92152d531bf5efa02030402bfc76a1212d32ab4f))

* fix : influxdb import ([`21f5652`](https://github.com/MyElectricalData/myelectricaldata_import/commit/21f56523e6f5caf5bdd9a91130e88c8eb30bf04e))

* mak release ([`4e92dae`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4e92dae01a4b0eb742c266e75339c4f9c680f207))

* Rename close_issue.yaml to close_issue.old ([`5dedd66`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5dedd668f13e54c16836360bd002a4a5b76aa2db))

* Rename issue_project.yaml to issue_project.old ([`213e6e9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/213e6e9ed7510d4b24b42b5611da00b178afdb7d))

* Merge branch &#39;master&#39; into 0.8.15 ([`59cfa18`](https://github.com/MyElectricalData/myelectricaldata_import/commit/59cfa18374c67e649db500c2dc904037c85e884e))

* Maj release ([`81d8bb9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/81d8bb90749255f499458768490dc7e1c472a09c))

* Update issue_project.yaml ([`13e278d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/13e278db80cd1492241b06af70954fc4ccafa9f2))

* Update issue_project.yaml ([`d651e78`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d651e78d78c622e94d66931515c971cfc598b383))

* Update issue_project.yaml ([`2b8a2a1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2b8a2a19cf11dc2ee129d12dfb13181f6fb6bb52))

* Update issue_project.yaml ([`01c13c8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/01c13c8a3e6a14d625aa178ac2d0e8d68091c35c))

* Update issue_project.yaml ([`bc2d293`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bc2d29383cae3c4b4f6286bced8c0215fe41c02d))

* Update issue_project.yaml ([`736181f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/736181fcbb4c33b2464c303b10d1b703bd118dcb))

* Update issue_project.yaml ([`413a723`](https://github.com/MyElectricalData/myelectricaldata_import/commit/413a723e54530d2cca6bc0851d3479b96db3f05f))

* Update issue_project.yaml ([`7c12888`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7c1288858a10b1fb8c5a8ad49f376247a91069d7))

* Update issue_project.yaml ([`1dc515c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1dc515c1d43655c7e1d92c5f0c94d1446faea445))

* Update issue_project.yaml ([`cb2337e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cb2337ed1c9c546e2d8dfc32ce19ccd0c29e64f5))

* Update issue_project.yaml ([`0080f0c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0080f0c9d0bcc106c75b6469eeb0c3f776abcfb6))

* Update issue_project.yaml ([`2035eda`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2035eda8516ea0f5a12a5f94d8ee9b0d06636ef7))

* Update issue_project.yaml ([`8d6eb9c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8d6eb9cc37083dd2e0025f90f7f6a883b16769ed))

* Update issue_project.yaml ([`001f057`](https://github.com/MyElectricalData/myelectricaldata_import/commit/001f057c64da0dbeb24762d72bb48260cba3acdc))

* Update issue_project.yaml ([`b5a351c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b5a351c1978c8be1c5ec6ef884e3f3943b350804))

* Update issue_project.yaml ([`a68d83d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a68d83df8f6d326d86754675e15ae8fa47b82e18))

* Update bug_report.md ([`bdb8ed7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bdb8ed71f5b95dfb53e8c0813d6b1d21a12f05ec))

* Update bug_report.md ([`7942c8f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7942c8f33cb28b79f778063aa1f93d89f9bdb388))

* Update bug_report.md ([`654769e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/654769e054b5df816ba0d6786c00ba8093ebfd49))

* Update bug_report.md ([`110b8ae`](https://github.com/MyElectricalData/myelectricaldata_import/commit/110b8aeb4298849e4fa5724df85556aaf261509b))

* Merge pull request #283 from m4dm4rtig4n/0.8.14

init 0.8.14 ([`ae087c0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae087c04503f4e9c94c9811bd416414ba2c6bb22))

* Release 0.8.14 ([`8038e6e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8038e6e84252b8dbdf8bba2d667aef27634f2df6))

* fix ([`545fedd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/545fedd80547f6c0773ef28bc8d5433a3fd2c7f3))

* typo config ([`ed771f7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ed771f78cd097b19337a4bf0d95604c9f20c2065))

* Update version ([`1f830dd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1f830dd847f679f175f5b35d5f5809f7f5cd39ba))

* add tempo ([`1fe4e92`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1fe4e92acb5801123095229bfce0705322d364f4))

* #285 + possibilité de boot sans pdl dans la config ([`3e6182b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3e6182b49bedab4331efa7c010f2b596a08c04bb))

* Update version ([`f7b2b7a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f7b2b7a2695789199c405b70ad13174a2ff23262))

* add log file + fix https://github.com/m4dm4rtig4n/myelectricaldata/issues/261 ([`8fe641d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8fe641dec3e3bcf11bcc021989c7ca0bd640c11f))

* test db.lock() at boot ([`eb895c0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/eb895c0b6e953582ab334fcc01a10945c4c3a5e2))

* init 0.8.14 ([`e336a51`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e336a510b7014b693757a5c067b8615461adb82b))

* Merge pull request #259 from m4dm4rtig4n/0.8.13

0.8.13 ([`54ed9e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/54ed9e690f63f6bf17cce0de6a962077b41815a0))

* Fix create-release ([`d9ed90a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d9ed90aaefbde8a4d7442fafeb54147469d95e3f))

* Fix create release ([`0477d9a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0477d9a2b54eed65e3b38c9ea0e35e0c33249cd3))

* Update Version ([`3fa44e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3fa44e6ba64e4ffe37903ca49d77ff3ef8f35afb))

* Update version ([`bed7f2e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bed7f2e52900f116165d28a2710aaf3c20a6d626))

* typo + fix ([`70df28e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/70df28e6fe2c461a416245d08f4e892d99ab4e4b))

* Merge branch &#39;0.8.13&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.13 ([`0624ef7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0624ef766b5f438ee3022829c8b318530d1e8929))

* Merge pull request #277 from vingerha/master

Fix last5days, add max_power to HA ([`063af0b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/063af0b4e20779c852a75e7850bbd9c072216d65))

* Update export_home_assistant.py ([`0a72502`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0a725024f2862550039e1c8e7745591b710228af))

* Update export_home_assistant.py ([`e7b511e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e7b511eadda43f6b196023cb36c9933eaf73e9af))

* Update export_home_assistant.py

J&#39;aurais tendance à préférer cette méthode.
Dit moi si ca fonctionne tjr chez toi. ([`d5a983e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d5a983e538eaf68ed70259bb088516fe7839f56e))

* Update stat.py ([`b50892c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b50892cfe52a04ef674c69acd1fd72731423eaf2))

* Update README.md ([`b1d3a01`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b1d3a011cdef9128e3fe2557f34a76bf21aef2c9))

* Merge branch &#39;0.8.13&#39; into master ([`12e1061`](https://github.com/MyElectricalData/myelectricaldata_import/commit/12e10617c47594bb5217b7532d447f139c17482c))

* Update version ([`976daca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/976daca1e830b7866cf7e2729cd0127e3e54a780))

* update charts + fix bug ([`28a21e0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/28a21e0f54483cf8b19bd8ed42108c2b7a0c993d))

* Add max_power_over

Allow to extracte truefalse, if max_power is over subscribed power ([`5678328`](https://github.com/MyElectricalData/myelectricaldata_import/commit/56783286822d1550e9ff68febde890b17911a842))

* Added max_power, fix for last5days

Last5days: was not exporting the whole of &#39;yesterday&#39; as referring to the current (today) time of day, removed the issue
Max_power: export max_power for past 7 days
Max_power_over: export where max power is &#39;over&#39; subscribed power (has dependency with stats.py update)
mp and mpo can be use in HA with Apexcharts and Saniho card (if accepted by Saniho) ([`ec31e33`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ec31e33d771eb97d8c39d21c7a2dfdca4077881d))

* Fix max date detail ([`a8f8c2a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a8f8c2a1a3a698b50aa779ac667a6879bc792d7e))

* Update README.md ([`bae064f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bae064f5e413f5510cc6be0b547fdd6ff5d6d9dc))

* Update README.md ([`74549a0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/74549a03cd9c4e45031206d48308a4ee301c4bbc))

* Update README.md ([`7caaa82`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7caaa82e499558476c1c8a48fa90811e5838cb7a))

* Update README.md ([`ebffc23`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ebffc23c8b701e74ad3538190b83e244bc90cc57))

* Update README.md ([`4edd1ba`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4edd1ba3c8e63ee7547f8d19a7e8c2864d2cf2aa))

* Rework datatable ([`5bfb383`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5bfb383623c789d460afea5d2e15d670cae427c0))

* Update version ([`6ffa48b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6ffa48b88c22254cbd227c815a8f101cf09d4ea0))

* clean ([`7506695`](https://github.com/MyElectricalData/myelectricaldata_import/commit/750669517e68a861ee50ff0a13d8ed5f00d6e0c7))

* test ([`a7420f9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a7420f90c50b659e93f227e131bc76b69ceb7912))

* init + issue 258 ([`9cc2ee6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9cc2ee6127093491be0f8d931e871383ed990505))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.12 ([`a0747bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a0747bc362deef4d1aca4c2a161f348074dfc95a))

* Merge pull request #246 from m4dm4rtig4n/0.8.12

0.8.12 ([`13b2fe0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/13b2fe0aa00f8b25f9c6b29c49850d12416a4b58))

* Release ([`91ee2a6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91ee2a6052fb04f1787bc09e1bc4221bd3a3e9ac))

* Update Version ([`ea82358`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea823587c061c26c8067ec67d0b8f495a62f5e56))

* rework mqtt data, fix stat, rename sensor,... ([`e4fd5e8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e4fd5e882cf80dde3db3b7de2202e3218ade4ba9))

* Update README.md ([`ae0cbef`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae0cbef4e5516576e5d825ceeacb641d4ac881c5))

* Update README.md ([`7a99369`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7a993698612588c6ae29870696bcd67660c1b6e2))

* Update README.md ([`7b47351`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7b4735172ad770f6652ef05e45dab8d98375d5d8))

* Update README.md ([`4945676`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4945676c5fce1b15b98e0b0b4b2829061530445b))

* Update README.md ([`10eca84`](https://github.com/MyElectricalData/myelectricaldata_import/commit/10eca84282df8013b19340a6e42f267a3c22f51b))

* Create FUNDING.yml ([`f51c4a9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f51c4a96626678a2d4840409dc316f5588520070))

* update version ([`8c29247`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8c292472a9cbeb9b07fb5ebe8d1b3d660e88e504))

* update version ([`8b07aaa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8b07aaaec85c2342697793476b0c73342821611e))

* edit contact db + fix ([`6945068`](https://github.com/MyElectricalData/myelectricaldata_import/commit/694506818eafd3a920679e5c2e1e9e3b2b5b62ff))

* maj ([`e39b429`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e39b4291a1d503d539efd41523e10b9769241c9c))

* maj ([`bdf19b5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bdf19b531d6a87d729e3270785634b89ce291a48))

* maj ([`dbbbedf`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dbbbedf413c1f96177c9d89cee6d087f1d2eb6fe))

* dashboard grah ([`7de3b2a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7de3b2aedf44f143f896c9eae49ce5faf760e03c))

* Update version ([`7246c72`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7246c72e0154234747106073fc1f76dc83af5376))

* Merge pull request #217 from m4dm4rtig4n/0.8.11

init 0.8.11 ([`9589480`](https://github.com/MyElectricalData/myelectricaldata_import/commit/95894804be963ab00f3c0dc5620b0f46722aa745))

* fix yesterday data ([`ae741b3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae741b3b2b592022fb6c255f751950eeb6c5f636))

* update version ([`d638973`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d6389732a4284fd2dac8140e0319c0e45411ff2c))

* fix last_activation_date ([`d03714e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d03714ef52e3cb83fc635745091b5f76950ce790))

* update version ([`a66eb52`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a66eb52bf223a63cbc37b9153c0c9f109b016753))

* minor ([`d004ae6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d004ae6d15113254614dd4e14b3987f41aaecd81))

* switch version ([`52a1f6b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/52a1f6b38915a56772ebf96a3c768bc8510c506e))

* rework mqtt export, add max power ([`876a1b4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/876a1b43bc8a796df613a3d0d2b2eddd66e88703))

* clean ([`2c6291c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2c6291c53a1e54a9bc14c8d952531dbfe6c63490))

* Update ([`02246fa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/02246faf47ab58d8f869b150be81b85c1f61d995))

* Beautify datatable ([`fd75c24`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fd75c2472f980e1ef11f1b96f53ee38b158056f1))

* fetch max power ([`fae3cb6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fae3cb6d86df1eeffcc058e30705bc3db6975a63))

* truncate float in enedis card ([`c2e9be5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c2e9be5a2e672f55bc726b4e378e18fee034b384))

* switch lock mode to file ([`a5b827b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a5b827b4960065fae2ebd8406b260e0fc421ca40))

* fix empty name + empty price ([`a570ba1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a570ba146a2d0802c286db5b05b545e5b6b6d044))

* update ([`5e70179`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e701790cd72d79b4965f67a93457f67f1a14e27))

* Merge branch &#39;0.8.11&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.11 ([`fed12a5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fed12a5926bdc4fae514bfd3f8e472e60aee2b87))

* loading screen ([`ad39c7d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ad39c7ddedb88fce09292ae203782903d0655ca9))

* Merge pull request #232 from evenisse/patch-18

Typo ([`e8b4857`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e8b4857074313f7a1e371f568fce84d9a747cda9))

* Merge pull request #233 from evenisse/patch-19

Typo ([`f806f98`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f806f989eaf5c754eb029b5ff0483814a133d0ae))

* Merge pull request #234 from evenisse/patch-20

Typo ([`c8d29ce`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c8d29ce147f74a929b56577bbe208397ad3f6ef5))

* Typo ([`5d6a8a6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5d6a8a679010ccb6f67d09aff0f7a463b6f1dee3))

* Typo ([`9e9195c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9e9195cc7e3cdc96013ae55b64b514c1377da205))

* Typo ([`eef163c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/eef163ce48882c1fffaab0b337b26a1f44741b0c))

* doc ([`d4d31a3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d4d31a3d1bd2e32aa25458a105e9b301cee2c584))

* new features ([`6c65a0a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6c65a0a6d1eb530af3be15f03a3fe2e36bb0bfee))

* Merge branch &#39;0.8.11&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.11 ([`5a6ba3e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5a6ba3e2b6c696ddbb7d93dced71c797055df734))

* test ([`4ada6cb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4ada6cbcb9adc1640a403d50300b53ba3c65b600))

* Merge pull request #228 from evenisse/patch-17

Clarification ([`fd19196`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fd1919687f29c1d32cd543e79aa0081eb5126709))

* Merge pull request #227 from evenisse/patch-16

typo ([`80a84b1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/80a84b1da8f334eab8537f1f7d2d6f4f2cfced2d))

* Clarification ([`e44b475`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e44b475b433c9d7ea6aee44e5b49d40d765e90c9))

* typo ([`972ede9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/972ede964a56b01f2c4a5c4222bb720e32fed790))

* init 0.8.11 ([`b70bfe6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b70bfe6d7b378bc1836fd86a4f938d5aaed7d954))

* Merge pull request #216 from m4dm4rtig4n/0.8.10

0.8.10 ([`5546986`](https://github.com/MyElectricalData/myelectricaldata_import/commit/55469869a8ff3e0d033b25f969727aedaf2c6ff7))

* init 0.8.10 ([`6f6f493`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6f6f49399f1da604e380adc7be4a6aaa7387274d))

* Update version ([`198ce01`](https://github.com/MyElectricalData/myelectricaldata_import/commit/198ce01036718998b252d59a37a8b005edc72bf5))

* Merge pull request #189 from m4dm4rtig4n/0.8.9

0.8.9 ([`4cb4442`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4cb4442c25fa3f58b927cbff5f53c8c9fc1c7d7d))

* Merge branch &#39;0.8.9&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.9 ([`79af69e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/79af69e99a5860aaf05eda1f3bfd23e18c892b05))

* Merge pull request #212 from evenisse/patch-14

Remove bad log that can generate exception due to unreferenced error ([`9947d6c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9947d6cc3dd178c2f73cabf2ce0781752791e053))

* Remove bad log that can generate exception due to unreferenced error ([`4b61477`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4b614779ea82dcc0500920c565fad5e02d2c2f30))

* Merge branch &#39;0.8.9&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.9 ([`623f7d6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/623f7d6bf96c7f093fa7930d82a250242a4a4af4))

* Merge pull request #207 from evenisse/patch-11

Fix influxDB 1.8 ([`730af78`](https://github.com/MyElectricalData/myelectricaldata_import/commit/730af78254263cc038f13ef27f73fdca3e377329))

* Create beta version ([`5831886`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5831886e855111702c19e8ec023f7d482935d6c1))

* Merge branch &#39;0.8.9&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.9 ([`95d61f9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/95d61f96f0341e97e63624e580861feaa19b0131))

* Merge pull request #209 from evenisse/patch-12

Remove bad log that can generate an exception due to unreferenced err… ([`8b8d095`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8b8d09575faf8f596bf6dede3aea13c88d88fd7d))

* Merge pull request #195 from pbranly/patch-8

Update ajax.py typo errors ([`5886c14`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5886c14e743154f656657be6f54e5c110c6b7c9f))

* Merge pull request #196 from pbranly/patch-9

Typo errors ([`be78fca`](https://github.com/MyElectricalData/myelectricaldata_import/commit/be78fca96005d76abcc9a8d279a9ae652bb43a4a))

* Merge pull request #197 from pbranly/patch-10

Typo errors ([`5541d75`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5541d75da1f9a7b765dcea81e9510ac69ecf2d1f))

* Merge pull request #198 from pbranly/patch-11

Typo errors ([`55e4c35`](https://github.com/MyElectricalData/myelectricaldata_import/commit/55e4c35fc02290225719b22967446b87b732ba35))

* Merge pull request #204 from evenisse/patch-9

Typo ([`d2788ac`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d2788ace3b700f6370e1c3d444c2d896aa43dbcf))

* Merge pull request #205 from evenisse/patch-10

Typo ([`a6dfb81`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a6dfb81355768368e26a6986d7b0a740465248cd))

* Merge pull request #210 from evenisse/patch-13

Typo ([`ae5ed66`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae5ed6626a5bb3e825a9c2f9adb6730a35469583))

* update to new gateway ([`85fe6e7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/85fe6e7ae9e3f6c5b8ce3546096a39d5a7ed051c))

* Typo ([`97d3a4f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/97d3a4f57990671f754b1fdf12f3ab6bc231c37b))

* Remove bad log that can generate an exception due to unreferenced error var

Log is done in the next if block ([`3b0c980`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3b0c980a8021ac4a16edd9b150984980fba26eaf))

* Fix influxDB 1.8

buckets_api.find_buckets().buckets isn&#39;t available for 1.8 ([`347d50b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/347d50b75678444af51d988ced57b92d54777c07))

* Typo ([`f91be15`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f91be15abf6a09b6272106a7991fea2725f3c1da))

* Typo ([`1a28a20`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1a28a2080f5e6533df413898d8a7b1e80e28e79e))

* Typo errors ([`132e2f1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/132e2f1da6e950c05adcf52b2aee329290d22087))

* Typo errors ([`fd3a291`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fd3a2912057e42e3e8dff485469df7bedd08ba43))

* Typo errors ([`4551d04`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4551d04bb682d5e6f1e370a693d71cf85ed6ddc6))

* Update ajax.py

Typo errors ([`b8a6bd9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b8a6bd9cec105a031d121760edda60ef0d8e03c5))

* Merge pull request #191 from evenisse/patch-8

Typo ([`1cc1c47`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1cc1c477cbd44acb720f395441acf905ba9f4a80))

* Typo ([`335d616`](https://github.com/MyElectricalData/myelectricaldata_import/commit/335d616c68f7313fecdf78a1027d4b21819533c4))

* reset gateway cache bouton ([`8c630c2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8c630c2329daeb7698b73dca9b162392cff667fe))

* init 0.8.9 ([`6aad378`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6aad37868a77184b2cc02f3875c24d009385e5e0))

* merge ([`7bd84eb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7bd84eb9abb822e6d6d277d9f57fffe1de162254))

* Merge pull request #166 from m4dm4rtig4n/0.8.8

0.8.8 ([`da5da9c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/da5da9cd0f1a4c291e1caf93e06ca8fe47b74da3))

* fix https://github.com/m4dm4rtig4n/myelectricaldata/issues/180 ([`cd33461`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cd334613b1ecfa321cbde4a1409b81fbc5a7ab23))

* fix https://github.com/m4dm4rtig4n/myelectricaldata/issues/180 ([`37e2e5a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/37e2e5a37c7a2087e30a42e097eedeb3853b20fb))

* maj doc ([`a90aae8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a90aae8841db86bf76699b072ed4b73cf471a96e))

* Merge pull request #181 from evenisse/patch-7

typo ([`3009112`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3009112bd126fb4dc2285dd648d91440a959949c))

* typo ([`0bfc6a9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0bfc6a992b707a28b7f4335b8dee338624a2f13f))

* fix https://github.com/m4dm4rtig4n/myelectricaldata/issues/143 ([`e147a04`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e147a046518261db3fd45fc2ebf786f1b876de16))

* Merge pull request #176 from pbranly/patch-2

Patch 2 ([`2432d03`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2432d03e3f2caaaf612a8d532ea082861528f369))

* Merge pull request #175 from pbranly/patch-3

Typo corrections ([`2f8be1b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2f8be1b8a12e9e3a049072796975aade8ed44a82))

* Merge pull request #177 from pbranly/patch-4

Typo correction ([`6bdffa0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6bdffa08e0689797a1f815d3fcdd976a77858a0d))

* Merge pull request #178 from pbranly/patch-5

Typo correction ([`b105edf`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b105edfd6b4955c2d24f8f64a2af237249d36fcb))

* Typo correction ([`c5f476a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c5f476a671f471bd879afd0e5d0f0760c38c1432))

* Typo correction ([`f10a800`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f10a800418c109ec10e386e36a318cead5464fd5))

* Typo corrections ([`a5ece87`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a5ece879e1b38e75569d84c15c4b34617705ddfb))

* Typo update ([`69c540a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/69c540abbd4cab003a9ee30ac505e2fbf275bdd4))

* fix influxdb infinite retention ([`8e7126d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8e7126dab3cdb12f3cf559993b7654fbfcf548b4))

* fix influxdb method ([`f6e28e7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f6e28e76f2b7ec16a73e626e9318ff976b25af02))

* remove 1 days delta ([`5b538e9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5b538e9f2629d86432a7ab8e63b6e73bd5036a9c))

* doc ([`f970c8f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f970c8f8274b08970cca7a64423e8d5b2b979737))

* fix unknow value in config.yaml, force float to export value in influxdb ([`786fffc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/786fffc9209cbf4493ac5aead12038b36705dc2b))

* fix Invalid header value b&#39;0.8.8-dev\n&#39; ([`2a01eb2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2a01eb209c7f8123764c2f27b72b0a4a87ae0acd))

* fix Invalid header value b&#39;0.8.8-dev\n&#39; ([`4c34684`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4c34684ef38795e78b0537a4342c261b2283dc48))

* Minor fix ([`b30181c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b30181c5acefbfd4539dc010c64013834b5192ba))

* Minor fix ([`c49d190`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c49d19039a2b34df924404449a5fa94a6a525e41))

* minor fiw ([`0a578ea`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0a578eaa8dbca5e9b78f56e729d60e29eb33e5e4))

* Add version in gateway status head ([`0080b31`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0080b3105d05f9a1644ee201fd7436258cd7346d))

* add switch version in CD ([`c2e4d86`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c2e4d860352b7016d8d10056321f3209f5cea1da))

* Merge pull request #163 from m4dm4rtig4n/0.8.7

0.8.7 ([`fbf6068`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fbf60680a0e951e7accb34cd3e5d1fab7015c902))

* Add other method to import data in influxdb ([`dca361d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dca361ddc84e25c7d5683d5c3f4010cca6434f2e))

* Fix CI ([`ca20d53`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ca20d5316efb22b6b8abf4cea2e36f1f1079c124))

* Fix CD ([`1d70daf`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1d70daf8e06db1f193df87b7dd20c0803bd4dc79))

* Fix CD ([`56d4988`](https://github.com/MyElectricalData/myelectricaldata_import/commit/56d498816fc524a0f541773bcd11fc4fa39ff522))

* release 0.8.7 ([`33a67c6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/33a67c6d434cfd4d198233aa958536ceea0ed909))

* test cd ([`63f6aff`](https://github.com/MyElectricalData/myelectricaldata_import/commit/63f6aff15e77f434843083b69f342e0479a0e404))

* Fix GH ([`ca06015`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ca0601565881ff3cd9245dbf64ef863f7cc5c835))

* Fix build latest ([`69510fd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/69510fda5dfcc5d8a7d8c5fc2ecec372c5f95bf8))

* Edit github action ([`db427fa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/db427fa070aa6978201b7d359e2510ce937293a0))

* Merge pull request #162 from m4dm4rtig4n/0.8.6

enable synchronous import on influxdb ([`4e040b2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4e040b265844ad2c8030d4b0e7bf82a0ce421b80))

* Skip import if all data is in cache ([`62e25fc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/62e25fcd149099d93f5a67aaaab81012d62b86aa))

* add https://github.com/m4dm4rtig4n/myelectricaldata/pull/151/files ([`ea1ae88`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea1ae883528c2906395458b631edcc5e50e883f3))

* fix production_detail_max_date &amp; consumption_detail_max_date ([`82c306e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/82c306eecc617c006829dd81f704811a8fbc70ad))

* fix production_detail_max_date &amp; consumption_detail_max_date ([`f634632`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f6346322e103d423e3c64d2534bb399fdd165ec3))

* Merge pull request #160 from m4dm4rtig4n/0.8.5

fix error on refresh contract + unit &amp; price in influxdb detail ([`6b54df4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b54df414bac9078df3fe13bd7750fe1b5cfadd3))

* enable synchronous import on influxdb ([`5a17a74`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5a17a74b3f0ac3c3d65dc3100bab0f5fe1211254))

* fix value in influxdb import + param in jobs ([`abfac74`](https://github.com/MyElectricalData/myelectricaldata_import/commit/abfac744a57289b7b080e18342a21879b1f3d83e))

* stop import if no measure found ([`53be9c7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/53be9c7600409a0508bddb41bfa481b734355ed1))

* fix wh calcul ([`8b028de`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8b028de6923e9e9154933fe8f29cde8b398f8c36))

* fix error on refresh contract + unit &amp; price in influxdb detail ([`05281a5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/05281a57f683ff3d8290995acfaa0114448b6129))

* Merge pull request #156 from m4dm4rtig4n/0.8.4

Merge pull request #155 from m4dm4rtig4n/master ([`b0e0700`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b0e0700100a2853d05dbca4f366add4f732f95d5))

* split activation date by mesure_type ([`c337980`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c33798027a0512b4a16ecd3f04259d6b829e6137))

* fix cache check for detail ([`eeef2c1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/eeef2c1196a97dcc82a70a83d12b2a5acfa1d646))

* add new column in usage_point ([`8e4e3ec`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8e4e3eca29eb634024c8b47ed5690b56cd5644d5))

* Merge branch &#39;0.8.4&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.4 ([`fa1fae6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fa1fae6876a547a13259fd4088af34ea8a46227b))

* export account status to mqtt ([`0db02dc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0db02dc142f8f63a1085cc583de4dbfb50ab138e))

* Merge pull request #155 from m4dm4rtig4n/master

Add PR ([`8423b50`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8423b502e4f5571fd9d5095bcd4f9f26eb0395d4))

* Merge pull request #154 from m4dm4rtig4n/revert-151-master

Revert &#34;Fix issue on error thrown on Keyerror &#39;base&#39;&#34; ([`8c4ba6e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8c4ba6eb207ce26814a1170c43433c42980a0c3b))

* Revert &#34;Fix issue on error thrown on Keyerror &#39;base&#39;&#34; ([`151f44c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/151f44c25419fea8da3bdf7d898976aa8e9c0dd6))

* Merge pull request #147 from m4dm4rtig4n/0.8.3

remove unit on datatables, fix bux + minor features ([`30ebc92`](https://github.com/MyElectricalData/myelectricaldata_import/commit/30ebc92c772d7df888103c865c6c18a845870a22))

* Merge pull request #151 from vingerha/master

Fix issue on error thrown on Keyerror &#39;base&#39; ([`6bfb70c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6bfb70cd69a779e25543885b4db4ba3fc0366f3f))

* release 0.8.3 fix ([`0c7cdc5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0c7cdc5d0450676162a65023ae58c46706088b39))

* release 0.8.3 ([`d002de9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d002de983adf2873fb6159a4e4dffbc0338afb95))

* Fix issue on error thrown on Keyerror &#39;base&#39; ([`e4338cd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e4338cd0d59874f66892f6f6fa08a764d7223734))

* Clean ([`39b7608`](https://github.com/MyElectricalData/myelectricaldata_import/commit/39b76083288b0f9b73f4d000baacfa4b62417cd3))

* remove no cache first call ([`ca383e5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ca383e5cedf2bacee625e5c6e961c8f124c59bd9))

* remove unit on datatables, fix bux + minor features ([`2ba3d77`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2ba3d77f6c5b0842536aadd29334d4e7a187112c))

* Merge pull request #142 from m4dm4rtig4n/0.8.2

0.8.2 ([`e9deb4e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e9deb4ec62dde801830127be82b6e339ffc7a27a))

* Disable boot import job only in dev mode ([`98ccbfb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/98ccbfbccd25f7b86a4a69d20bc2b94ef0573bcc))

* Switch Flask server in production mode ([`00c5a8c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/00c5a8c7493cab235d095a18e0aa0020984f605c))

* Merge pull request #141 from m4dm4rtig4n/0.8.1

0.8.1 ([`94c5de3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/94c5de3182fc19097b6a928be2eee064d37a1584))

* Update config.exemple.yaml ([`cf3001a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cf3001a5971ee5065e866fa236da7a99042c8044))

* Update config.exemple.yaml ([`6ba5557`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6ba5557976074968801eb36e5de523d6a5476d7f))

* Merge pull request #132 from m4dm4rtig4n/0.8.0

0.8.0 ([`4a54da2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4a54da2aacfd510024f63ca24c4c38ca5e472187))

* Fix HA evolution sensor when not value ([`d94a84f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d94a84f0f8828ffeca2edd3f3bfcc4c632eec422))

* Enable job at boot ([`fda3897`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fda389784e91f76584a4d507dd37e5f096dbf57d))

* Fix bug on fetching data ([`f76cca4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f76cca4e43aee09682bd6b289cd24aaf212e96e5))

* Fix HA evolution statistique ([`4711bdb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4711bdbcd595aa00f064603e5f27aceb784bc614))

* Merge pull request #138 from evenisse/patch-5

typo ([`1ffbdc1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1ffbdc1f01df9c76316f1b8b6f516b27fef44cf7))

* Stop import if quota reached, rework stat in Home Assistant export ([`662979c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/662979c68d72e4785f0701b62cacd80e4d514825))

* maj ([`f1b530e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f1b530e8ab9e90ce1f0e0e6268abec01db57afad))

* typo ([`d6d84da`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d6d84da86f7a411cb4f1a419fe8bfe1a5f0448dd))

* maj ([`7f75b7a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7f75b7a49ef96fddcb3743712a20572d392d8dab))

* maj ([`94c0cb9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/94c0cb97d52737b220afdcce7cffd5917815b1cb))

* maj ([`9a60666`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9a606663e8d100027a7bad7f07a7c3c051559355))

* maj ([`d913ad3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d913ad3a94ffe246d43db9fa78e94800821ef614))

* Merge pull request #136 from evenisse/patch-4

Missing enable field on PDL ([`0ec21a3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0ec21a302c6b702bd5e80876cd8742419db77edf))

* maj ([`c07a70c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c07a70cd618e78c758f19f0958c809e655e514c0))

* Missing enable field on PDL ([`8ba08da`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8ba08da26d59efd5ba828324ddfe6e9767e1e43c))

* Missing enable field on PDL ([`aa8cea9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/aa8cea993693fa127f0e7ed4733ad6a89e438141))

* Merge branch &#39;0.8.0&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.0 ([`f02c51e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f02c51e366f97eb474693cca3e294e016f251f5b))

* Test CI ([`a29dcd9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a29dcd9db2c9547202e73b414de3ff83af223558))

* Test CI ([`684b287`](https://github.com/MyElectricalData/myelectricaldata_import/commit/684b2870de1af862491a61c97a1b66b2d89bad9a))

* Test CI ([`3d92a68`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3d92a6833e7787ba035e22b160094f3c652dde61))

* Test CI ([`fa3d7fa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fa3d7fa2fd9fa54c11b8307b242ed25b078a16a8))

* Test CI ([`ef411ee`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ef411ee029d3e0232e764b081edeaada210c60cb))

* Merge pull request #133 from evenisse/patch-3

Typo ([`640ece7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/640ece7b8415c657a70d9c792d02bc77f382c251))

* maj ([`b081b71`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b081b711e521b40a36014c9e3fd30d677a26ab31))

* maj ([`cf68984`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cf689849094edb06c0b6cd5d805bdd77e6979d12))

* maj ([`7f22d71`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7f22d71847461a5f1f4a4f650710bbb51c67a44c))

* maj ([`fdcebb7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fdcebb7c45692d2791bd81d3bf4759810eb9984c))

* maj ([`7c48dda`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7c48dda0db4cfd82a81e9088328899485e27d555))

* Typo ([`a5d1a9b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a5d1a9b59e7a823b076aabf27f754156f0eb48fc))

* maj ([`011bef0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/011bef0272048a939399171842061457adf7ad87))

* maj ([`aa282d1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/aa282d143d37fd5960bb46ef126245bc5544aa32))

* maj ([`9284b69`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9284b69d06f7ffe8c22739033fbb2c4a3f948ed5))

* Merge branch &#39;0.8.0&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.0 ([`7a71df7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7a71df78e49f3c124a4a8c37102c7b62b979b0e5))

* Merge branch &#39;0.8.0-dev&#39; of github.com:m4dm4rtig4n/myelectricaldata into 0.8.0 ([`66c8a75`](https://github.com/MyElectricalData/myelectricaldata_import/commit/66c8a7557f55eecfd4ce4521f20fe8ea22faa87c))

* maj ([`488915d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/488915db0ae27c4dde3538c10399a4cdf1bedd9f))

* maj ([`a0e5556`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a0e5556a9a1e97f0e6d15dfa941081c6c9da0126))

* maj ([`e5dd900`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e5dd900b9d4d5adf68eee1cb0c49588f2f47455a))

* Merge pull request #131 from evenisse/patch-2

typo ([`0c046d3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0c046d369e47c6b300462e6cc992215cb6234812))

* typo ([`ce25951`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ce259511e11502d3166a7b2f2cdcd7c80cec8162))

* typo ([`c2d11f4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c2d11f403e6996c8e6cb8be0a4b8fec42ab84be2))

* maj ([`118067b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/118067b41ecb29219499169a1c264e7d748caac1))

* maj ([`01292bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/01292bcaf73699398174bac6e895098ea80c569f))

* maj ([`ea51e52`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea51e521d6c272ee708a6a28f4bad159c4c84013))

* maj ([`8d8eb56`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8d8eb5647e416f71d68366914f408d6f14d44d99))

* maj ([`9291deb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9291debdb88108eeadbc9dbd25871ce48fed0cdd))

* Merge pull request #129 from evenisse/0.8.0-dev

typo ([`d8dd599`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d8dd5993b84e63c4d3c4fbc85e5d86307cdabcae))

* Use python:3.9.7-slim ([`34201fc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/34201fc10402c31d9cd36ac7d90f6b3f1e5bf4fc))

* typo ([`9180010`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91800107b19863e3ee01208320ef61a103fd8d97))

* maj ([`8d2c4b8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8d2c4b82c19dda25dafe4177a4bda5db7c14e271))

* maj ([`773fd25`](https://github.com/MyElectricalData/myelectricaldata_import/commit/773fd25dc2d81de127a2d32e7fd7e3d435da8fca))

* maj ([`0c77842`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0c778428b9ca0da22422e92d3fcd1d15d28c7357))

* maj ([`6b83c4a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b83c4a24c833c3bdb270d01fb1c97e9acdb83a9))

* maj ([`9cd3695`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9cd369568ebd1a1467812c24aa5038686b00ead9))

* maj ([`0b8f441`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0b8f44107db418cc71f4aba98d6b928dafec17cc))

* maj ([`ea78687`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea78687f047c6c2a502ca2ebd977831aff02538a))

* maj ([`4faf60a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4faf60a57ba18ede35d674a830283d58cf08c127))

* maj ([`8a13072`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8a13072231716035c6768a107389b29229795cd1))

* maj ([`84e51c3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/84e51c39d7d3ac2166a1dd57f97ca38e2a5d73f3))

* maj ([`89f9363`](https://github.com/MyElectricalData/myelectricaldata_import/commit/89f9363c8b9612bb5d1b96a4b237167edd7bf89d))

* maj ([`26e8337`](https://github.com/MyElectricalData/myelectricaldata_import/commit/26e833761e79753d331689ad4d4c6cc441f3b6f5))

* maj ([`e5a4faa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e5a4faa95e0e7e91ae8d6ce9314f2317ceb0a43f))

* maj ([`f2bf3c9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f2bf3c93c1cddba7548efdd197b426b27dd4d014))

* maj ([`8b79f42`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8b79f42fd95b35665e95bc2f6bfaf4fd9b716446))

* maj ([`3f276c9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3f276c92deaf28949520188c29d32b6f6bb53992))

* maj ([`bb6f0cd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bb6f0cdcb17bbc6bda075083d63980f332afe60c))

* maj ([`041efb1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/041efb19cef0669eadb37da5bed9f0bbf864a306))

* maj ([`91d595f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/91d595fecf5cec15b5f2bfa19462b2750fdeda71))

* maj ([`22ee656`](https://github.com/MyElectricalData/myelectricaldata_import/commit/22ee65651486705bf67a6ee9841e29792c388675))

* maj ([`926ef21`](https://github.com/MyElectricalData/myelectricaldata_import/commit/926ef2105b62118f74ed275591c81a4a4377c048))

* maj ([`0120638`](https://github.com/MyElectricalData/myelectricaldata_import/commit/01206389bbc67a77f9d6e6226c0d4b4b670bab27))

* maj ([`7063343`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7063343e670e3194704015c37d2f45cc73618c44))

* maj ([`5820b61`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5820b612ace9a585e1b9401b7715b6218ac256a1))

* maj ([`de291fa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/de291fa48a920b3e0facf6adb2abf749f2be70bd))

* maj ([`74057b8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/74057b808e7c0bfddc54000b3235466652f67b3b))

* maj ([`1ecc4e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1ecc4e639c433e0c321b8acd7a5e2749364e810d))

* maj ([`316c217`](https://github.com/MyElectricalData/myelectricaldata_import/commit/316c217ad1afc378a5366f22372d0c64fda0eea7))

* maj ([`82468e4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/82468e48384f20a4186ac0fb6492c6a944675956))

* maj ([`b5d1a02`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b5d1a028157033718bbae5d370e57ab90f5860c0))

* maj ([`a991a6d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a991a6d5837aaf030020aa52b588e6a65030f84a))

* maj ([`bcf9be1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bcf9be16db8cac277e5c4e65fa43ae2e1af6bcdb))

* maj ([`d9473c3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d9473c373275fbe74e6882e22cdb4c8b71e66558))

* maj ([`1095757`](https://github.com/MyElectricalData/myelectricaldata_import/commit/10957576ce88dd8ebce2d9501c281afc699ab53e))

* maj ([`3710b3a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3710b3af3f5b0d1e0f9ba57c872e0d7abe3e00df))

* test ci ([`772ba26`](https://github.com/MyElectricalData/myelectricaldata_import/commit/772ba26cd4945e3c64c7dd555fd4450ebc801417))

* test ci ([`3815953`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3815953473faeb74b0b260440a6527b8a8cb5458))

* maj ([`c5c00bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c5c00bcd75c0b6dc5ab6c4b6b50b2fe7edd11b34))

* fix yesterday_HCHP ([`12f7a7d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/12f7a7ded2c6f9af94f66f0066882d468edf8c57))

* influxdb scheme ([`4a77f66`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4a77f66eef2ae8100ab2e9ec3360d557bb59a65b))

* Merge pull request #88 from cvalentin-dkt/patch-1

Update README.md ([`0694521`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0694521f7d2ffb2f373da67282582586e287379d))

* Update README.md ([`77d9fd2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/77d9fd2f7d71b15df1fa8ca5110b5764dc28792f))

* upgrade lib influxdb ([`87c1647`](https://github.com/MyElectricalData/myelectricaldata_import/commit/87c16473d7a6b8fd3869ae06cf8084257ee8033d))

* test tz ([`e3067e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e3067e61032d2a9014bcecdf5ca482955d04621e))

* Merge branch &#39;0.7.8&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.8 ([`8213b9b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8213b9b8e37d3c225542794f4493c6ce601a41b1))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.8 ([`e0f50ab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e0f50ab8137a5e2a9662d41fd6cf6932aaa72292))

* fix timeout ([`c17a2b8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c17a2b8c3c6b5299bea7537b98e69599509d1104))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.8 ([`e187fa8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e187fa8ae0f623860b4055a61bf71699b2fd3c39))

* mah ([`bc5fc7b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bc5fc7b2237aed8bc2aa793f3ef551a069bf4648))

* fix \n ([`75d94ae`](https://github.com/MyElectricalData/myelectricaldata_import/commit/75d94ae166225eb5e0e9ce96d8e24390b9882bb2))

* init 0.7.8 ([`94e82b6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/94e82b60617d22b0dd2a46320c0a7eac1820b9b8))

* init 0.7.8 ([`181d2c4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/181d2c4907bb8c1af7b25ad4253bbda62b4a899d))

* init 0.7.8 ([`cfbd46b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/cfbd46b5c187a6a61e43431f28f68582d3612555))

* Merge pull request #69 from m4dm4rtig4n/0.7.7

0.7.7 ([`18ccfb1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/18ccfb106faddad060ea3c908b5ec20820d036c3))

* 0.7.7 release ([`3778ad6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3778ad615e026af13d565a4c66ba7f8ffa46209c))

* 0.7.7 release ([`fa70f23`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fa70f23e5ea4588842cbd2e197e69726f0eed0f5))

* 0.7.7 release ([`fea3a41`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fea3a414a232823639163d702d0f2b1279e41ddc))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.7 ([`4247998`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4247998fb6cb5872d6a12906fb0297cd345bb11b))

* 0.7.7 release ([`13e0838`](https://github.com/MyElectricalData/myelectricaldata_import/commit/13e0838a4334f8dbfb78c4705bcb3412b76ef51a))

* Update README.md ([`b6695d3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b6695d326268eb2e891117832b4c55da3a8da490))

* Update README.md ([`aab8c1d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/aab8c1ded0160fb363efb12557d1b418fd52e616))

* Update README.md ([`46e3c28`](https://github.com/MyElectricalData/myelectricaldata_import/commit/46e3c289e6b7db80ee07426a12e190cba0aa1708))

* Update README.md ([`902ec6e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/902ec6ed15d16785cf897e4109de38a5c0c5f426))

* Update README.md ([`7294b9f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7294b9fd56cc8c27e635bf283fe5ec9ff79a7fdd))

* 0.7.7 release ([`ba8bacc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ba8bacc748b2394e72febfe15971c574bb304c77))

* 0.7.7 release ([`0bfe389`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0bfe389316aa7a50247405d954c52c35022d57fa))

* Update issue templates ([`0f59e23`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0f59e23766f6474b889471249d39a8905137bc1b))

* Update issue templates ([`2d73261`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2d73261834e2e7e7874cc7184984c7301c73d617))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.7 ([`b0a890a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b0a890aac5b98f71074959a71cb999267f693ca1))

* maj ([`5e92e57`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e92e57099405c5f26cbed2ef7cb83da5a8fed14))

* Update README.md ([`df753b9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/df753b947f984543e47016dc16930ce3cc3f3284))

* Update README.md ([`ee828c0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ee828c04ad3e835a9b375234eac1f47726a8272b))

* Update README.md ([`3debbf2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3debbf258b62c109ade44801c48df929c63ff7c5))

* fix hc/hp calcul ([`93fd5b5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/93fd5b54b95b79c501f70cd18ba80ac507885e99))

* Update README.md ([`fe8ed19`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fe8ed19b33743244f4192889254d6b18b6ee3433))

* fix reset data when multiple pdl ([`1b80d34`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1b80d34bdddb8fb4eba76cf17a1f9f5f4ffe4529))

* fiw offpeak ([`1f98d3b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1f98d3b267d96c79d5ffd098729111477aeaf05a))

* Update README.md ([`c94574e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c94574effba27dd8d371324d54d6e4ecc01bb59e))

* fix #48 ([`7ff2f46`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7ff2f469b9d7eb2264afef79afa8704768f3aee3))

* fix #45 ([`978c1ab`](https://github.com/MyElectricalData/myelectricaldata_import/commit/978c1abf0febdc11d9065e3c87d9898f01a710c9))

* Update issue templates ([`58888eb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/58888eb3c40cbb036531a10ab1996216b13a6b1d))

* Update README.md ([`642bac2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/642bac2af49f927dffe37a51292b0e223ff148dd))

* Update issue templates ([`9d355bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9d355bcab26704f91a065b91e45ff4dbe0d2ad31))

* fix db corrumption ([`8f1297e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8f1297ede41fbca424c9f3a9ce4a4024cc97f0aa))

* fix db corrumption ([`82c0327`](https://github.com/MyElectricalData/myelectricaldata_import/commit/82c0327adb3c68cb79a59d9a047a390977f6d54e))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.7.6 ([`354376e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/354376ea9531450a854f3cfb4dd1049ada829452))

* fiw init db ([`fa1ccad`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fa1ccad85a1954e4f07e0404c1a8f93f895266c3))

* Merge pull request #61 from m4dm4rtig4n/0.7.5

rework config ([`0d09a16`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0d09a163d44fbd19da787b3fe1b8e1ae39a42055))

* rework config ([`965f26c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/965f26c093bb32d7fcfe853429d20195183e0d23))

* Update issue templates ([`d9fd685`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d9fd6857266188026445fe22a25e21f0b6c979e8))

* Update issue templates ([`faf8b18`](https://github.com/MyElectricalData/myelectricaldata_import/commit/faf8b183c40fe74ca6b58dffa5b9670d34fba954))

* Update issue templates ([`c7c9291`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c7c92919dd4d66176aae0de88b7eb1133f2365db))

* Merge pull request #59 from m4dm4rtig4n/0.7.4

maj doc ([`c49a912`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c49a9122644dbe51f8251777a9543fdeb41c87d6))

* maj doc ([`fd151a8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fd151a8e37b88f1f51be093c9802075b1260b889))

* Merge pull request #57 from m4dm4rtig4n/0.7.4

0.7.4 ([`643c6d5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/643c6d5db375c05f62dfb1042965ccd589e8ce32))

* fix sqlite closed connection ([`ed5b10a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ed5b10a1cb940a7f03218ace0b2467756c8b9ec3))

* fix header ([`a0707c0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a0707c0f655bf64147c8b659842ffc50348c0972))

* Merge pull request #53 from m4dm4rtig4n/0.7.3

0.7.3 ([`9d3b41b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9d3b41b4dea1dc54cd4179a6d5a5350128bf81c5))

* Merge pull request #51 from m4dm4rtig4n/0.7.2

0.7.2 ([`b65eea1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b65eea10c55e7403e69f400a7daf2bc3a666d790))

* update doc ([`07cb9df`](https://github.com/MyElectricalData/myelectricaldata_import/commit/07cb9df482b5fdb2ef975cba265da468abfd8b49))

* fix debug ([`9692fb5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9692fb5994fe59a58d0cefefe40aabf8d2a03689))

* fix version ([`7f843bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7f843bc08f699b97adddbdf623db5e9511ba6f90))

* fix offpeak_hours: 0 ([`2fde425`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2fde425755a17aa00f83be93f9309bf0dc730685))

* Merge pull request #47 from m4dm4rtig4n/0.7.1

clean ([`c8d34d9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c8d34d972918a9e58728b31dffc3b05fd9fa5e68))

* fix ci/cd ([`ddff86d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ddff86de63eb2be8497f7f69c21c071f260af426))

* fix ci/cd ([`e8a68d9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e8a68d902ce6bd89bbde2f08321aa485e046ab12))

* merge ([`9fe7bc8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9fe7bc833f101a869b6c30784c32524cde05a15c))

* release 0.7.1 ([`49d7d03`](https://github.com/MyElectricalData/myelectricaldata_import/commit/49d7d03175c294b1345f6529c7209104d479a6f0))

* release 0.7.1 ([`701574c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/701574c82401579db904b655fa33766fcf354ff2))

* Merge pull request #50 from alexbelgium/patch-4

Avoid date issue ([`ec7bb44`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ec7bb445a1de6c008323b204fe2dd14280edd807))

* Avoid date issue

https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/48 ([`e472727`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e472727b2bb16bf65affccdb5ee863aa19b0a760))

* fix ci/cd ([`0dd8753`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0dd8753c1e187fff5d8152e4f4fbcd8b7691ef4b))

* fix ci/cd ([`f66e0b4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f66e0b437d7f13255ebe81f0d228449aca8a4b17))

* fix ci/cd ([`da87a2a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/da87a2a9749ab5e015fe2e913311841cbea866ea))

* fix ci/cd ([`93d652a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/93d652aa79d4e55f691e3ba1a82e42022f9d39c8))

* 0.7.1-dev ([`a11630f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a11630f85815f57f0b71888220525cd014190074))

* check parameter ([`1772b9c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1772b9c1bbccf0bbd6893c24c804529afc0600f2))

* maj ([`25cba34`](https://github.com/MyElectricalData/myelectricaldata_import/commit/25cba34481d079e5d71b1556d4f256a2e887d5c7))

* maj ci/cd fix ([`934f3a8`](https://github.com/MyElectricalData/myelectricaldata_import/commit/934f3a87568a39b40bf15c24591e0bfad1450ae9))

* maj ci/cd fix ([`2234e80`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2234e80b43cefc14869fa5b7f6f78bc1bc6f058f))

* maj ci/cd fix ([`a65122b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a65122b82a98668f0057228f7a376e7a8be35683))

* maj ci/cd ([`8ad2647`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8ad264759463e4a71515aec78ad890ae8ba02c3d))

* daily ok ([`4a895ee`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4a895eeb178698748bb89fd0ef336d92b2d462b3))

* clean ([`04e3e98`](https://github.com/MyElectricalData/myelectricaldata_import/commit/04e3e980a7942e9208d407febb9a7d70a56da85f))

* clean ([`2e985ea`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2e985ea9ad387e7ad3b4246068172ea1d4920fa8))

* release 0.6.0 ([`225ec94`](https://github.com/MyElectricalData/myelectricaldata_import/commit/225ec946cf50dc0d464e0b742a17f5b02c31eac9))

* add link ([`f444253`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f444253c926e03da8374c4f6fd669afe1bd9ba7d))

* hassOS addons ([`2e954a1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2e954a18aae527aa78f8536275b072253f12f34c))

* fix ([`294d821`](https://github.com/MyElectricalData/myelectricaldata_import/commit/294d8214cef305949375126da6b99aeb197f208e))

* Merge branch &#39;0.5.6&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.5.7 ([`a7a78f5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a7a78f586a9859d6b74b5e799e326a6e9907fdbe))

* 0.5.7 ([`96b6d2c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/96b6d2cd7f2a56be4ef569aab117d3dea4ecab0e))

* fix bug ([`bbfdd2c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bbfdd2ce6848bd990e5382f5df065d6bfe541820))

* fix bug ([`fbde995`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fbde995b41939dd38b7e6c31aedb47ea55cd801b))

* 0.5.6 ([`691b88c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/691b88cd466eb3978ab9889c3e5afb9d0b11cb0d))

* notif ([`5dd708e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5dd708e0becb00f071db4da9c402f9cfe084f584))

* check var ([`8e0164f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8e0164f7b192513f8800c8511c03c1a6eb9adbbf))

* fix mqtt ([`ac492f9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ac492f989fce13a6eb465c94047988b7e0a6007c))

* 0.5.5 ([`0f23e50`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0f23e50a485c20a84e70ee6143590f993c10fdfa))

* maj readme ([`416003f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/416003fe350f99e86fb300e003db958018ab042a))

* release 0.5.4 ([`7665be1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7665be1c1427502150d4c00d827ed42f2ebfb379))

* release 0.5.4 ([`6b71d6c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b71d6c1d673cec2748c89e850d0bed265dca494))

* Smeagolworms4 pr ([`fc522a7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/fc522a7fa08625531857c79fbca00f595d04b937))

* Smeagolworms4 pr ([`e9376e7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e9376e7c538915819d25f2b2ffd626ccdde2f417))

* Merge pull request #29 from GollumDom/ha_discovery_add_device_and_cut_path

HA Discovery: Add device Linky and cut path ([`feac6a0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/feac6a00ac4a753d48a2ebea920ade1a17891d67))

* Merge pull request #28 from GollumDom/dev_setup

FIx Dev setup ([`1da05a0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1da05a0fa88ab51f699f11eb927dd6d6c3c983d9))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.5.4 ([`c4577cd`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c4577cd55e93e8d2fbbc407cc9a9ba40dd3fbc9a))

* HA Discovery: Add device Linky and cut path ([`55f3bc3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/55f3bc3219d0c63ed51b7d4f6511fff10fddf8c3))

* Add dev environment auto configuration ([`4282855`](https://github.com/MyElectricalData/myelectricaldata_import/commit/42828550b83e1870c038e0866e760b415e7101dc))

* Add dev environment auto configuration ([`bc8e659`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bc8e659406b60e3494acad8d97c0e11cbe39ac38))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.5.4 ([`c2a880a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c2a880a36299512ee2526a2527d894627090a5e9))

* Merge pull request #27 from GollumDom/dev_setup

Add dev environment auto configuration ([`e5e2d31`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e5e2d316e0596138316f3184dcd30b4a65e29af5))

* Add dev environment auto configuration ([`304453c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/304453cbcfe1de9a04dc1cc852dcb0994738b0bc))

* latest-dev ([`06cc7c4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/06cc7c44948663eaa71e400313a9d1610c37736d))

* 0.5.4 ([`0780d08`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0780d08b9bca9086a265cba59ec4077328fbee0d))

* 0.5.3 ([`20a4c4a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/20a4c4a544031c4362be3aa517275e9a92ba9354))

* Merge pull request #24 from m4dm4rtig4n/0.5.2

maj doc ([`afc20e3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/afc20e393e0cc38ed70a68e49e8bdc4fce45947e))

* maj doc ([`6b43f4d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b43f4dac6771078f319d785c321f3f8d74e97e1))

* Merge pull request #23 from m4dm4rtig4n/0.5.2

0.5.2 ([`f7fb116`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f7fb11619f00707712892b9179c66ba901bb8941))

* maj doc ([`73d5ad4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/73d5ad4a0cd3c48809ba3f6bbf129ab182287aa7))

* fix offpeak ([`bed69fc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bed69fcae6df065b2048b9ccf367ff9402d873c6))

* Merge pull request #22 from m4dm4rtig4n/0.5.2

readme ([`b70f29e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b70f29e0d62679216bec8dc198be413a6f5ba3e9))

* readme ([`6b4545e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6b4545e9b83fca2ae0f0bb08ba8d83a80558dfd3))

* Merge pull request #21 from m4dm4rtig4n/0.5.2

0.5.2 ([`723e109`](https://github.com/MyElectricalData/myelectricaldata_import/commit/723e109a5871356048bea7074b60ec984978a7d3))

* readme ([`7ed030d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7ed030d6797d9624caf36de551f232764cb0b889))

* remove influxdb params ([`8de9b1e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8de9b1e7fe5ce9e88ef684ebd78ed276e43a32a9))

* add influxdb check connexion ([`d6aecf7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d6aecf7455ba3aae77f38c78c19b548e1f0869ae))

* add debug influxdb ([`64e4024`](https://github.com/MyElectricalData/myelectricaldata_import/commit/64e4024ab5cf4a76cdec87341a40a1d59c78e5d0))

* Merge pull request #20 from m4dm4rtig4n/0.5.2

0.5.2 ([`1bb5681`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1bb5681ae3547abe27a7fa7f4296a284d793c2ea))

* 0.5.2 ([`77614e6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/77614e6f1ec7755bb416fe6f248a90f38635e66a))

* influxdb test ([`6634336`](https://github.com/MyElectricalData/myelectricaldata_import/commit/66343365e2c0357c4bb2db03164fc502baae19c8))

* test ([`42d9a80`](https://github.com/MyElectricalData/myelectricaldata_import/commit/42d9a80b4793a35d67492f9b1b7e4609c2bb6537))

* clean ([`f76fb42`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f76fb42b1b9512a80b6897c8478e26b79c185dff))

* merge ([`dec50c7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/dec50c7660c526f7392fcc2af20c2052010f2b8a))

* fix ([`e4aeabc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e4aeabc3765c2e65556a4c5493d5a7483df254ce))

* influxdb init ([`860b430`](https://github.com/MyElectricalData/myelectricaldata_import/commit/860b43019088b08866eec9709a617ea22b667504))

* influxdb init ([`6511f10`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6511f1091de301327aa5e48057e934b67cf61846))

* fix ([`83168f6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/83168f6d12ef7129b21ef1f0c46965bf7f65401f))

* fix ([`61bce8c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/61bce8cce373e54ad6c01a35bb8eb5eb03273039))

* fix pip ([`1eba9f6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1eba9f648bc57e932d334fb2521c16aa78a4e653))

* Merge pull request #19 from m4dm4rtig4n/0.5.1

0.5.1 ([`de2b0f6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/de2b0f6fee3f84250db5abf2b295cbc447d68a80))

* fix pip ([`0313da0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0313da0dc486df990c955af1060264c684ea4fe9))

* fix pip ([`7593485`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7593485d8421e0966723f4454c89a11216c761fb))

* Merge pull request #18 from m4dm4rtig4n/0.5.1

0.5.1 ([`d81d99d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d81d99d4293c2cbdf8c6a4d7d4f9a3ae4a23b0f1))

* fix ([`0cddab3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0cddab3b49190271904de40f494ad1412b7bc4a8))

* fix ([`049c156`](https://github.com/MyElectricalData/myelectricaldata_import/commit/049c1567c60b0f4cebd4532680c2444e2becfdd5))

* Merge pull request #17 from m4dm4rtig4n/0.5.1

0.5.1 ([`60fe637`](https://github.com/MyElectricalData/myelectricaldata_import/commit/60fe637c3fd3ca7cb6f8743e7e093d51597f473e))

* fix ([`4bdc4d4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4bdc4d4e7b430d5d35d13a4d8e1fd84bc78bba3e))

* Merge pull request #16 from m4dm4rtig4n/0.5.0

0.5.0 ([`038927e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/038927e79181e1eaf47bf86c42d1045d8fa16498))

* clean ([`5e97542`](https://github.com/MyElectricalData/myelectricaldata_import/commit/5e9754262679f6c25a86ac5911773e5d15df19f2))

* Create HA sensor for Linky Card with auto-discovery ([`75b3cee`](https://github.com/MyElectricalData/myelectricaldata_import/commit/75b3cee8d9566294d37e30eb516a0a9d0c123691))

* fix config table ([`80db8a4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/80db8a48f72a4d89d96d1c79e8bcf68ce58afa69))

* release 0.5.0 ([`b108ecf`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b108ecf58c76a987b11e52d7db7e17be78d81a34))

* fix ([`79fb5ba`](https://github.com/MyElectricalData/myelectricaldata_import/commit/79fb5ba3e99de26333e4ae13094e19f88ae93b70))

* fix ([`ae754b7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ae754b752d02452db8c7346717c7459587fdfc95))

* fix error return ([`8263f58`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8263f583f30ef03fa06a71a7e473c6c184ddeb0e))

* remove scipy ([`c66097f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c66097f01d5b84f5713c6994ed1c79fc2a8c26c0))

* remove scipy ([`8a2b5bc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8a2b5bc85bb1d08b0043bf2edf0f234ffa3a3385))

* pre-release ([`3f640a5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3f640a5410f118cb8a13d7d650b055e7299917b8))

* hc/hp ([`b7e21d7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b7e21d749fe001a2429e8b04cd5534c52f20efe6))

* 0.5.0 ([`247552c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/247552c038c1bbc28a5e45d56c84f22417cb2ce4))

* Merge pull request #15 from m4dm4rtig4n/0.4.1

init 0.4.1 ([`1a4b698`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1a4b698ded94c1a154bf4af270be46296893e5c9))

* init 0.5.0 ([`daccec2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/daccec2af3191a31ca2c03103863a6c12fee83ce))

* cache addresses &amp; contracts ([`3fab84b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3fab84b5a8e2b47667fdc27ba3ce4bdf9c26781a))

* fix ([`34d4005`](https://github.com/MyElectricalData/myelectricaldata_import/commit/34d40053bc7b6fb73c430ad4be78bac80468ec74))

* cache addresses ([`249e71a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/249e71a43a66ff78a76f6e1657189cd12a6455d6))

* test ([`87edf2f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/87edf2f02ed8b4364a9cb961c7c07bbab4462c14))

* init 0.4.1 ([`96148ff`](https://github.com/MyElectricalData/myelectricaldata_import/commit/96148ff9d53be02312b3a01f58818e9c4c5975bd))

* Merge pull request #13 from m4dm4rtig4n/0.4.0

0.4.0 ([`50cefb3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/50cefb38f3e2cbc70301fbc7cd3a37ad450e402d))

* clean ([`ed442df`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ed442dff7c8c295ee2a7ead306e4703cd14483a0))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.4.0 ([`1fa570c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/1fa570c90c8a2c75ef9ca6b612ba8d4126d06905))

* Merge pull request #11 from m4dm4rtig4n/0.3.2

fix ha discovery bug ([`c58799d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c58799de9440665eb209427877e2887d424aeb75))

* lot of change, go readme.md ([`49a31db`](https://github.com/MyElectricalData/myelectricaldata_import/commit/49a31dbd5c5db0d3560fec848ce0689e28bfa146))

* Merge branch &#39;master&#39; of github.com:m3dm4rtig4n/enedisgateway2mqtt into 0.4.0 ([`8a89921`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8a89921bd0acc38e12f278d8081b0094996663a6))

* lot of change, go readme.md ([`0da96f5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0da96f53c91018a4b76d3b09c1489e33f780557b))

* maj adr ([`d3b6b05`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d3b6b058ce0bcd757fed9a6010a9599da3aa2809))

* Merge pull request #12 from Jeoffreybauvin/hotfix/fix_compose

Fix compose booleans and restart policy ([`b29e188`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b29e188435466dc8b2a129a9a1a3ea8de200db29))

* Fix compose booleans and restart policy ([`9fe4c3c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9fe4c3cbf7c609c512b78d2189124a3ae48ef353))

* update ([`7d4d65f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7d4d65fc0d3a2be36154a75a4cce1e8bcef89a46))

* fix ha discovery bug ([`4b62637`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4b62637de4259cf0ba894521316ebddf3c40320a))

* Merge pull request #10 from m4dm4rtig4n/0.3.1

maj ci/cd ([`06e2e6a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/06e2e6a3987e66f31501a792a4d026a9875c3641))

* maj ci/cd ([`a75721b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a75721bad6141a1ea3c17c69f7d78e54e889a3f0))

* Merge pull request #9 from m4dm4rtig4n/0.3.1

Fix error when API call limit is reache ([`060065b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/060065bf999e6becaf0905dceabb8861663cbe0a))

* Test discord notif ([`c0a19b9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c0a19b9f1713116fe08b48dec20d7b818539c6fd))

* Test discord notif ([`0eee113`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0eee113d5981ac601c7e2dd1a69bb8dd61efca9c))

* Fix error when API call limit is reached. ([`ef8632f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ef8632f80912cc983dab2bd433bb0acfc7aa1841))

* Merge pull request #8 from m4dm4rtig4n/0.3

switch to python-slim ([`d910050`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d91005057912f251b60ffa0c489cd66866b49599))

* switch to python-slim ([`99554f0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/99554f0c81dabd7be5b9bb4b7f9dff31320e861e))

* Merge pull request #7 from m4dm4rtig4n/0.3

0.3 - fix ([`4e705a6`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4e705a6dd6f494118bf1e75e6e034cb3a2e7fd62))

* clean ([`32c633a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/32c633a24a385e22a7077e5c342f8b03fbd52250))

* fix ([`471e67b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/471e67bdeaab07eb9e7428dbf069f52e848b1fa2))

* Merge pull request #6 from m4dm4rtig4n/0.3

rework ha autodisco ([`48b9b3b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/48b9b3b6ebd785e86a2387a4a431e55c40d6edf6))

* clean ([`9debdbb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9debdbb53d84cd7f70ffb2d1d965aa0391ba7ff3))

* clean ([`72a58f3`](https://github.com/MyElectricalData/myelectricaldata_import/commit/72a58f3f842bf6802a2f942157978d43bba8ab86))

* release 0.3 with SQLite, Production, and HA Rework ([`6470ac5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6470ac50cb2d396efb566b0ab2508e89eaf47b7b))

* maj ([`bab2cf2`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bab2cf2fd8dd5d62b9c508d9e48e02227663eacf))

* clean ([`8e338cc`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8e338cccddada4b57bf201cd9edadfea2c11d723))

* integrate sqlite ([`e115382`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e11538296827769b58d870d79efda7b4b4e95850))

* Merge branch &#39;0.3&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.3 ([`e63bc0c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e63bc0c0a5f971e62076c73b527193fff808a6ff))

* switch env vars + fix ([`0f73433`](https://github.com/MyElectricalData/myelectricaldata_import/commit/0f73433550dc8d6304b5f429e7ddd60f58841f22))

* maj ([`e36f00e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e36f00e0036abde1ba5263e3264e33cad51c3f04))

* Merge branch &#39;0.3&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.3 ([`b8a01eb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b8a01eb4f9f9ea175d3922cfe4b0492bf470b38e))

* Merge branch &#39;master&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.3 ([`e4686c5`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e4686c51ea1f0872e7d06bef47d46dc58fe4b67a))

* switch env vars + fix ([`efc1a42`](https://github.com/MyElectricalData/myelectricaldata_import/commit/efc1a422fdae7ff844464588e41228d6325b92a0))

* rework ha autodisco ([`053c010`](https://github.com/MyElectricalData/myelectricaldata_import/commit/053c010d25242e85dcaaadcd4e4699738d2f3e06))

* rework ha autodisco ([`4802d95`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4802d959da2e7fe653f125b8f4bc005e35a5c004))

* Merge pull request #5 from m4dm4rtig4n/0.2

0.2 ([`667799e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/667799e3dcec28522e2aba4f5c8e8a48f5e252cd))

* add dynamic qos ([`e25fd3f`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e25fd3fa2f1bdfaf35a4d3f87b67de4e0ca59aeb))

* add dynamic qos ([`9875f79`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9875f79f6bd0a1038d82ab29fab3a9234185f6ed))

* add dynamic qos ([`98a6745`](https://github.com/MyElectricalData/myelectricaldata_import/commit/98a674590b39552bc4dd91300cfc8cc83d44f011))

* add dynamic qos ([`36845e9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/36845e948e62110d48dde87b387bbe27fd57b94f))

* rework gh action ([`8e76d35`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8e76d3507cf31b5cf483982cc29da9ab7672ef97))

* add timestamp + retain + auto discovery HA ([`74d9021`](https://github.com/MyElectricalData/myelectricaldata_import/commit/74d9021d6f2bd16828372ed9b029cf4e790aae59))

* chart-helm + dev version in ci/cd ([`9303247`](https://github.com/MyElectricalData/myelectricaldata_import/commit/930324793d55288c335905423fb501f858718c2c))

* chart-helm + dev version in ci/cd ([`d115562`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d11556201eec05c3ae9537eaf82e79ebdab8f151))

* chart-helm + dev version in ci/cd ([`036e23d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/036e23dd8605ab8f05166bafed9d9ae09e39a846))

* chart-helm + dev version in ci/cd ([`3e80808`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3e80808f970718c2699b306b775dd48f66a19857))

* chart-helm + dev version in ci/cd ([`ba2286c`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ba2286cd073c8fb2d762739bdf86a82509b7ea58))

* chart-helm + dev version in ci/cd ([`b068377`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b0683777186f2370661452c691d86eef5ddbfc61))

* chart-helm + dev version in ci/cd ([`bc5995b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/bc5995bc188a56031271a226e47fdd4baf53431a))

* chart-helm + dev version in ci/cd ([`a53cf86`](https://github.com/MyElectricalData/myelectricaldata_import/commit/a53cf8689f7a7241e094e7deca93985309a6c6cd))

* auto pr ([`e1068d1`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e1068d13ea899054127b50bce7f0ded896043e20))

* auto pr ([`41836cb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/41836cbd38568dc89e557d90e522e7f26db575e5))

* auto pr ([`ea90c9b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ea90c9b17ff038455345aaba8e83ddb3f5e88ed5))

* auto pr ([`d532dee`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d532dee7720d01e0515fcebeffba86fe4b6da1c3))

* auto pr ([`7f67f85`](https://github.com/MyElectricalData/myelectricaldata_import/commit/7f67f85c7c17ef547e91e981af29e1e94b47681e))

* auto pr ([`976ce94`](https://github.com/MyElectricalData/myelectricaldata_import/commit/976ce94b61d606c52e465b6f95afaa3c8e5da418))

* auto pr ([`8671e0b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/8671e0b9491861ca8a308c500ecefa8dd6f4c6f0))

* auto pr ([`2bdc004`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2bdc0040828b1d66d7fcb9e945a57f39a84ab34b))

* auto pr ([`e8d7011`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e8d701146592c5cad7c589a76f7c8a5b7d2e39aa))

* Update report

Signed-off-by: GitHub &lt;noreply@github.com&gt; ([`ff31119`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ff31119ba457d677f70d2b6e29d3bf9703867044))

* Update report

Signed-off-by: GitHub &lt;noreply@github.com&gt; ([`6edcdb9`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6edcdb902de0c14ca424c1a7276a8bbbaadf09ae))

* auto pr ([`76b4ea0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/76b4ea052f64a683dbbcfd63a2a7a02305f90432))

* Merge branch &#39;-1.1&#39; of github.com:m4dm4rtig4n/enedisgateway2mqtt into 0.1 ([`b4170cb`](https://github.com/MyElectricalData/myelectricaldata_import/commit/b4170cb47826758fe5ccb1a4c590a276c25b51d4))

* auto pr ([`e733aaa`](https://github.com/MyElectricalData/myelectricaldata_import/commit/e733aaabbbf9db9cdb19e5779ab232502dcd28c1))

* Update report

Signed-off-by: GitHub &lt;noreply@github.com&gt; ([`f6a724d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/f6a724d462da52472bf4a58afd4b44c98f7db4fb))

* Merge pull request #1 from m4dm4rtig4n/master

[Docker] build master ([`074fad7`](https://github.com/MyElectricalData/myelectricaldata_import/commit/074fad71589001434bd0f1fc2dba1424cbfb6044))

* auto pr ([`3c15799`](https://github.com/MyElectricalData/myelectricaldata_import/commit/3c157996008a58d061a327de30bdff1886084086))

* Update report

Signed-off-by: GitHub &lt;noreply@github.com&gt; ([`44d0d08`](https://github.com/MyElectricalData/myelectricaldata_import/commit/44d0d08ac4731e915590e8fdc16a0c3904a45304))

* auto pr ([`16783f4`](https://github.com/MyElectricalData/myelectricaldata_import/commit/16783f4f82465b0f104c46bacf0416ad8d38332f))

* auto pr ([`6e2ae17`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6e2ae17f0fc7bc852209b80777e921173eaa3ec3))

* add armv6 &amp; v7 ([`be7ba49`](https://github.com/MyElectricalData/myelectricaldata_import/commit/be7ba49ab0129c738542cf4d632fa157724e7338))

* add armv6 &amp; v7 ([`997c312`](https://github.com/MyElectricalData/myelectricaldata_import/commit/997c312dd863502e09c1a39ba70f25b143f427f1))

* add armv6 &amp; v7 ([`274e07d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/274e07ddef246c32972e5f36d7df0f747832a17b))

* ci/cd v0.1 ([`c8cec74`](https://github.com/MyElectricalData/myelectricaldata_import/commit/c8cec74086ad8ef16c7e1f69931afeb061517e86))

* ci/cd v0.1 ([`4a0baf0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/4a0baf06773f08bab7e79af5ad6eb94c3a209000))

* test ci/cd ([`d6a899b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/d6a899bcaf3fb9d83d795f85aef8dd2e423b2a77))

* test ci/cd ([`ee8736b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/ee8736b35edf06badb824c5292e7a06e295e1687))

* test ci/cd ([`12a7645`](https://github.com/MyElectricalData/myelectricaldata_import/commit/12a7645cc0d2b3cd117200821d567bdfaa02501e))

* test ci/cd ([`9f0bdb0`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9f0bdb062501dd1fab50062ae98e2bebf2d90e38))

* test ci/cd ([`6dff15a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6dff15acde10e68fa0cbc2ee609b57b76240abb6))

* test ci/cd ([`6c6178b`](https://github.com/MyElectricalData/myelectricaldata_import/commit/6c6178bbe17db104cdfd5da23ee1aa7792404332))

* test ci/cd ([`2334d8a`](https://github.com/MyElectricalData/myelectricaldata_import/commit/2334d8a86e48f7c16ec53d4e8773ef39dc85efe0))

* ci/cd ([`808a06d`](https://github.com/MyElectricalData/myelectricaldata_import/commit/808a06d7e6fe6f50e5ce93aa503a8c9b50db1e1e))

* init ([`11c1311`](https://github.com/MyElectricalData/myelectricaldata_import/commit/11c1311d5bc0840e90206e361b2ff44a3e5747fb))

* first commit ([`9f1978e`](https://github.com/MyElectricalData/myelectricaldata_import/commit/9f1978e485d1cfb523fa003c0f49887bd3890184))
