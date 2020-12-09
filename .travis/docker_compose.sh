#!/usr/bin/env bash

# Pull alpine base image from docker hub, but then retag it for $cr_server for reuse.
docker pull "library/alpine:3.11" || true
docker tag "library/alpine:3.11" "${cr_server}/wikipedialibrary/alpine:3.11"
docker pull "${cr_server}/wikipedialibrary/twlight_base:${BRANCH_TAG}" || true
docker pull "${cr_server}/wikipedialibrary/twlight_build:${BRANCH_TAG}" || true
docker pull "${cr_server}/wikipedialibrary/twlight:${BRANCH_TAG}" || true

docker build --cache-from "${cr_server}/wikipedialibrary/alpine:3.11" \
             --cache-from "${cr_server}/wikipedialibrary/twlight_base:${BRANCH_TAG}" \
             --target twlight_base \
             --tag "${cr_server}/wikipedialibrary/twlight_base:${COMMIT_TAG}"  \
             --tag "${cr_server}/wikipedialibrary/twlight_base:${BRANCH_TAG}"  \
             --tag "${cr_server}/wikipedialibrary/twlight_base:${BUILD_TAG}" \
             . && \
docker build --cache-from "${cr_server}/wikipedialibrary/twlight_base:${BRANCH_TAG}" \
             --cache-from "${cr_server}/wikipedialibrary/twlight_build:${BRANCH_TAG}" \
             --target twlight_build \
             --tag "${cr_server}/wikipedialibrary/twlight_build:${COMMIT_TAG}" \
             --tag "${cr_server}/wikipedialibrary/twlight_build:${BRANCH_TAG}" \
             --tag "${cr_server}/wikipedialibrary/twlight_build:${BUILD_TAG}" \
             . && \
docker build --cache-from "${cr_server}/wikipedialibrary/twlight_base:${BRANCH_TAG}" \
             --cache-from "${cr_server}/wikipedialibrary/twlight_build:${BRANCH_TAG}" \
             --cache-from "${cr_server}/wikipedialibrary/twlight:${BRANCH_TAG}"  \
             --tag "${cr_server}/wikipedialibrary/twlight:${COMMIT_TAG}" \
             --tag "${cr_server}/wikipedialibrary/twlight:${BRANCH_TAG}" \
             --tag "${cr_server}/wikipedialibrary/twlight:${BUILD_TAG}" \
             . && \
docker-compose -f docker-compose.yml -f docker-compose.travis.yml up -d db twlight
