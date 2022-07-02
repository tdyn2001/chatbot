'use strict';
const AWS = require('aws-sdk');
var ecs = new AWS.ECS();

module.exports.hello = async (event) => {
  console.log("s3 uploaded!")

  var params = {
    cluster: "chatbot_cluster",
    enableECSManagedTags: true,
    launchType: "FARGATE",
    count: 1,
    platformVersion: 'LATEST',
    networkConfiguration: {
      awsvpcConfiguration: {
        assignPublicIp: "ENABLED",
        securityGroups: ["sg-0a4a4ce8a86e23e65"],
        subnets: [
          "subnet-0525a921ebb66fe68",
          "subnet-0ce7d0661e5b38dbc",
        ]
      }
    },
    startedBy: "ecs_task_execution_role",
    taskDefinition: "training_task_def"
  }

  console.log("Starting execution...");
  await ecs.runTask(params).promise();
  console.log("done.")
};
