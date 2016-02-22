#!bin/bash

cd ..
mvn clean package
cp target/java-sky-1.0-SNAPSHOT.jar bin/
