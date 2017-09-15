
.PHONY: check-groovy
check-groovy
	ssh -p 8089 localhost declarative-linter < build.groovy
