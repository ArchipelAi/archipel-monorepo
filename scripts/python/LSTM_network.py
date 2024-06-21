#####
#####
#####
#PRELOAD FUNCTIONS



import json

def auto_generate_feature_vector(response_outputs, num_step, problem_scope, problem_type, n_models, adaptation_rate, num_steps_proposed):
    """
    Generate a feature vector based on the responses and environment complexity.

    Args:
    - response_outputs: List of responses from the models.
    - num_step: Current step number.
    - problem_scope: Scope of the problem.
    - problem_type: Type of the problem.
    - n_models: Number of models.
    - adaptation_rate: Rate of adaptation (default is 0).

    Returns:
    - feature_vector: A tuple containing the feature vector.
    """
    # Initialize lists to store scores
    fitness_scores = []
    act_max_scores = []

    # Evaluate fitness for each response
    for response in response_outputs:
        response = response[num_step]
        text = list(json.loads(response['message']).values())[0]
        ag_rationality, model_type_label, agent_type_label = orep.evaluate_fitness(response["model_type"], response["agent_type"], problem_type)
        fitness_scores.append(ag_rationality)

    # Calculate consensus score
    consensus_score = orep.calculate_consensus_score(response_outputs, num_step)

    # Calculate action maximization scores
    for fitness in fitness_scores:
        ag_rationality = fitness
        act_max_score = orep.calculate_act_max_score(ag_rationality, consensus_score)
        act_max_scores.append(act_max_score)

    # Select the best response
    best_response_index = act_max_scores.index(max(act_max_scores))
    best_response = response_outputs[best_response_index]
    best_response_backup.append(best_response)
    model_type = best_response[num_step]["model_type"]
    model_type_label = {"gpt-3.5": 1, "gpt-4": 2, "gpt-4o": 2, "gemini": 3, "gemini-ultra": 4, "mistral": 5}[model_type] #convert model type to label

    act_max_score = max(act_max_scores)

    messages = [best_response]
    error_rate = orep.evaluate_error_rate(messages[0][num_step]['message'])
    best_response_body = list(json.loads(best_response[num_step]['message']).values())[0]
    print(best_response_body, error_rate)

    problem_scope_label, problem_type_label, num_step, n_models, num_steps_proposed, ratio_steps_left = orep.evaluate_environment_complexity(
        problem_scope, problem_type, num_step, n_models, best_response_body, num_steps_proposed)

    # Generate the feature vector
    feature_vector = (
        act_max_score,
        ag_rationality,
        model_type_label,
        agent_type_label,
        adaptation_rate,
        problem_scope_label,
        problem_type_label,
        num_step,
        n_models,
        num_steps_proposed,
        ratio_steps_left,
        error_rate
    )

    return feature_vector, best_response_body

##########

def process_steps(response_outputs, best_response_body, num_step, problem_scope, problem_type, n_models, adaptation_rate, num_steps_proposed, sub_layer=0, finished=False):
    bullet_markers = ['-', '*', '•']
    finished = finished
    
    while not finished:
        feature_vector, response = auto_generate_feature_vector(response_outputs, num_step, problem_scope, problem_type, n_models, adaptation_rate, num_steps_proposed)
        training_data.append(feature_vector)

        task_step = best_response_body[num_step]
        num_step += 1
        
        response_outputs_backup.append(response_outputs)
        response_outputs = []

        orep.openai_request(client, n_models, num_step, system_task, task_step, response, response_outputs)
        print(response_outputs)

        if any("FINISH" in output for output in response_outputs):
            return True

        # If the response contains sub-steps, process them recursively
        for response in response_outputs:
            response_body = json.loads(response[num_step]['message'])
            if 'steps:' in response_body['message']:
                sub_steps = []
                for line in response_body['message'].split('\n'):
                    if any(line.strip().startswith(marker) for marker in bullet_markers):
                        sub_steps.append(line.strip())
                
                if sub_steps and sub_layer == 0:
                    sub_response_body = ", ".join(sub_steps)
                    if process_steps(response_outputs, sub_response_body, num_step, problem_scope, problem_type, n_models, adaptation_rate, num_steps_proposed, sub_layer + 1):
                        return True

    return False

##########

def contains_finish(response_outputs_backup):
    for response in response_outputs_backup:
        if isinstance(response, list):
            for sub_response in response:
                for key, value in sub_response.items():
                    if 'message' in value:
                        message = value['message']
                        if isinstance(message, dict):
                            if any("FINISH" in msg for msg in message.values()):
                                return True
                        elif isinstance(message, str):
                            if "FINISH" in message:
                                return True
        elif isinstance(response, dict):
            for key, value in response.items():
                if 'message' in value:
                    message = value['message']
                    if isinstance(message, dict):
                        if any("FINISH" in msg for msg in message.values()):
                            return True
                    elif isinstance(message, str):
                        if "FINISH" in message:
                            return True
    return False

#####
#####
#####


#LOAD LIBRARIES
import oracle_repo as orep
import importlib
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer, util
import yaml
import os
import openai as OpenAI
import openai
import json

#INITIALIZE DATABASES
response_outputs_backup = []
training_data = []

#GENERATE A RESPONSE OBJECT
response_outputs = []

#PRECONFIGURE THE PARAMETERS
#Initialize parameters
adaptation_rate = 0 #initialize adaptation rate.
messages = [] #cache to store list of best_responses for each request iteration t.
training_data = []
best_response_backup = []
num_steps_proposed = 0

# DEFINE THE PROBLEM TYPE
# Example usage with user input

# problem_types = ["deterministic", "predictive", "code_based", "philosophical"]

# print("Choose problem type:")
# for p_type in problem_types:
#     print(f"- {p_type}")

# # Get user input for problem type
# problem_type = input("Enter the problem type: ").strip().lower()

# if problem_type not in problem_types:
#     raise ValueError("Invalid problem_type provided")

problem_type = 'deterministic'

# problem_scope = ["open", "closed"]

# print("Choose problem scope:")
# for p_type in problem_scope:
#     print(f"- {p_type}")

# # Get user input for problem type
# problem_scope = input("Enter the problem type (open or closed problem?): ").strip().lower()

# if problem_scope not in problem_scope:
#     raise ValueError("Invalid problem_type provided")

problem_scope = 'open'



#INITIALIZE FIRST AGENT SEQUENCE

# Load the YAML file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Get the API key from the YAML file
api_key = config['openai']['api_key']

from pathlib import Path
import time
    
# Initialize the OpenAI client
client = openai.OpenAI(api_key=api_key)

#initialize request parameters
n_models = 2
system_task = "Invent rules for a board game with a scoring system on a 1-step scale and play that game until you reach score 5. Respond with 'FINISH' once a player has reached score 5. Do not ever mention the word 'FINISH' unless a player has reached 5 points."#
#"Order a Pizza near the Giesing Brewery in Munich. Deliver it to the following address: Arcisstraße 21, 80333 Munich, Germany. Payment with be handled by a human upon arrival of the pizza. Respond with 'FINISH' when you are done."task_step = system_task
num_step = 0
response = "Null"
task_step = system_task

orep.openai_request(client, n_models, num_step, system_task, task_step, response, response_outputs)

fitness_scores = []

for response in response_outputs:
    response = response[num_step]
    text = list(json.loads(response['message']).values())[0]
    ag_rationality, model_type_label, agent_type_label = orep.evaluate_fitness(response["model_type"], response["agent_type"], problem_type)
    fitness_scores.append(ag_rationality)

# Calculate consensus score
consensus_score = orep.calculate_consensus_score(response_outputs, num_step)

# Calculate the action maximization score for each response
act_max_scores = []
for fitness in fitness_scores:
    ag_rationality = fitness
    act_max_score = orep.calculate_act_max_score(ag_rationality, consensus_score)
    act_max_scores.append(act_max_score)



#RUN BENCHMARKS ON OUTPUT
fitness_scores = []

for response in response_outputs:
    response = response[num_step]
    text = list(json.loads(response['message']).values())[0]
    ag_rationality, model_type_label, agent_type_label = orep.evaluate_fitness(response["model_type"], response["agent_type"], problem_type)
    fitness_scores.append(ag_rationality)

# Calculate consensus score
consensus_score = orep.calculate_consensus_score(response_outputs, num_step)

# Calculate the action maximization score for each response
act_max_scores = []
for fitness in fitness_scores:
    ag_rationality = fitness
    act_max_score = orep.calculate_act_max_score(ag_rationality, consensus_score)
    act_max_scores.append(act_max_score)


# # Output the scores
# for i, response in enumerate(responses):
#     print(f"Response from {response['model_type']} - Agent Rationality: {fitness_scores[i][0]}, Act Max Score: {act_max_scores[i]}")


# # Output the scores
# for i, response in enumerate(responses):
#     print(f"Response from {response['model_type']} - Agent Rationality: {fitness_scores[i][0]}, Act Max Score: {act_max_scores[i]}")

# Select the best response
best_response_index = act_max_scores.index(max(act_max_scores))
best_response = response_outputs[best_response_index]
best_response_backup.append(best_response)
model_type = best_response[0]["model_type"]
act_max_score = max(act_max_scores)

messages.append(best_response)

#calculate error rate
error_rate = orep.evaluate_error_rate(messages[0][num_step]['message'])
best_response_body = list(json.loads(best_response[num_step]['message']).values())[0]


#calculate env_complexity
problem_scope_label, problem_type_label, num_step, num_agents, num_steps_proposed, ratio_steps_left = orep.evaluate_environment_complexity(problem_scope, problem_type, num_step, n_models, best_response_body, num_steps_proposed)


#generate feature vector

feature_vector = act_max_score, ag_rationality, model_type_label, agent_type_label, adaptation_rate, problem_scope_label, problem_type_label, num_step, n_models, num_steps_proposed, ratio_steps_left, error_rate

training_data.append(feature_vector)


#UPDATE REQUEST PARAMETERS
task_step = best_response_body[num_step]
num_steps_proposed = len(best_response_body)
num_step =+ 1
response_outputs_backup = response_outputs
response_outputs = []

orep.openai_request(client, n_models, num_step, system_task, task_step, response, response_outputs)

#INITIALIZE SUBSEQUENT RUNS

finished = False
sub_layer = 0

finished, sub_layer = process_steps(response_outputs, best_response_body, num_step, problem_scope, problem_type, n_models, adaptation_rate, num_steps_proposed, sub_layer)
