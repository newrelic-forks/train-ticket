#!/usr/bin/env bash
set -eux

echo
echo "Start Pushing images, Repo: $1, Tag: $2"
echo
for dir in ts-*; do
    if [[ -d $dir ]]; then
        if [[ -n $(ls "$dir" | grep -i Dockerfile) ]]; then
            docker push "$1":"${dir}"-"$2"
        fi
    fi
done
