

podman run --rm -v $HOME/.aws:/root/.aws:ro -v .:/app --network aws-net -e AWS_DEFAULT_REGION=us-east-1 aws-secrets-tools python secure_connect.py