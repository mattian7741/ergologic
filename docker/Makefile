all: clean build
synch:
	echo "building components from ${QED}"
	rsync -avr --exclude='*/.qed-mq/*' --exclude='.git*' --exclude='*.idea*' --exclude='*.terraform*' \
		--exclude='*node_modules*' --exclude='*.serverless*' --exclude='*venv*' --exclude='*__pycache__*' \
		${QED}/ ./.qed-mq/


#TODO: need a better way to do xplatform building and testing
build-local: clean synch
	DOCKER_BUILD_KIT=1 docker build --ssh default \
	--build-arg manifest=${component}.yaml --build-arg comp=${component} \
	--build-arg qed_dir='.qed-mq' \
	--platform linux/amd64 -f ergo.Dockerfile -t ${component} .

build-ac: clean synch
	DOCKER_BUILD_KIT=1 docker build --ssh default \
	--build-arg manifest=api_connector.yaml --build-arg comp=api_connector/${vendor} \
	--build-arg qed_dir='.qed-mq' --platform linux/amd64 \
	-f ergo.Dockerfile -t ${vendor}_api_connector .


build: clean
	git clone git@github.com:nautiluslabsco/qed.git ./.qed-mq
	docker build --build-arg manifest=${component}.yaml --build-arg comp=${component} \
	-f ergo.Dockerfile -t ${component} .

clean:
	rm -rf ./.qed-mq

app_env ?= "qa"
run:
	#docker run -it --env APP_ENV=$(app_env) ${component} nautilus_docker.yaml
	docker run -it --env APP_ENV=$(app_env) ${component} ../../../namespaces/nautilus_docker.yaml

inspect:
	docker run -it --entrypoint /bin/bash ${component}

test-ssh:
	DOCKER_BUILD_KIT=1 docker build --ssh default -f test/ssh.Dockerfile -t ssh_image --no-cache .
