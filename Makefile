.PHONY: build build-base check-updates release

# Manual app-image build/publish, versions passed explicitly.
# Usage: infisical run -- make build base=1 relatorios=v0.8.01.1 execucao=v0.5.27 reest=v0.2.8 [push=1]
build:
	./scripts/build_image.sh --base=$(base) --relatorios=$(relatorios) --execucao=$(execucao) --reest=$(reest) $(if $(push),--push,)

# Manual base-image build/publish. Base bumps are deliberate and infrequent.
# Usage: infisical run -- make build-base n=2 [push=1]
build-base:
	./scripts/build_base_image.sh --n=$(n) $(if $(push),--push,)

# Report whether relatorios/execucao/reest have newer GitHub tags than what's
# baked into the published :latest image.
check-updates:
	./scripts/check_updates.sh

# Check for updates and build+push a new app image if any are found.
# Used both locally and by the daily CI schedule.
release:
	./scripts/check_and_build.sh
