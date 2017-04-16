
.PHONY: check
check:
	ssh -p 8089 localhost declarative-linter < build.groovy
