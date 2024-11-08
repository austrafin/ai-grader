#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
  echo "Use script as: ./clone_student_projects_all <DESTINATION> <ALLOCATION FILE> <GIT NAMESPACE>"
  exit 99
fi

mkdir -p $1
cd $1

IFS=','

{
  read # Skip header line

  while read AssessorFirst AssessorLast StudentId Language SubmissionUrl Hash
  do
    echo -n "Cloning $StudentId ... "
    git clone "git@course-gitlab.tuni.fi:$3/$StudentId.git" -q
    cd "$StudentId"
    # Hash might have a \r at end. Let's ditch everything past 40 chars.
    git checkout "${Hash:0:40}" -q --
    echo ""
    cd $1
  done
} < $2

read -n 1 -s -r -p "Cloning finished - press any key to continue"
