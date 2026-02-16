#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

git rev-list --count HEAD
