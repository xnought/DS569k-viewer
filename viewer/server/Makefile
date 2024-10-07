all: requirements noversion

requirements:
	toml-to-req --toml-file pyproject.toml

noversion:
	cat requirements.txt | awk -F'[>=<>>= ]' '{print $$1}' > requirements.noversion.txt