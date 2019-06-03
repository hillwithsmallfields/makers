cmd_config_help() {
    cat <<_EOF
    config
        Run configuration scripts inside the container.

_EOF
}

cmd_config() {
    ds inject debian-fixes.sh
    ds inject install-system.sh
    ds inject install-makers.sh makers.yaml /opt/makers
}
