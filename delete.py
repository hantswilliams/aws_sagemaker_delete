import boto3
import time

sm = boto3.Session().client('sagemaker')

def list_sagemaker_experiments():
    results = sm.list_experiments(MaxResults=100)
    output = []
    for result in results['ExperimentSummaries']:
        output.append(result['ExperimentName'])
        print(result['ExperimentName'])
    return output


def cleanup_boto3(experiment_name):
    trials = sm.list_trials(ExperimentName=experiment_name)['TrialSummaries']
    print('TrialNames:')
    for trial in trials:
        trial_name = trial['TrialName']
        print(f"\n{trial_name}")

        components_in_trial = sm.list_trial_components(TrialName=trial_name)
        print('\tTrialComponentNames:')
        for component in components_in_trial['TrialComponentSummaries']:
            component_name = component['TrialComponentName']
            print(f"\t{component_name}")
            sm.disassociate_trial_component(TrialComponentName=component_name, TrialName=trial_name)
            try:
                # comment out to keep trial components
                sm.delete_trial_component(TrialComponentName=component_name)
            except:
                # component is associated with another trial
                continue
            # to prevent throttling
            time.sleep(.5)
        sm.delete_trial(TrialName=trial_name)
    sm.delete_experiment(ExperimentName=experiment_name)
    print(f"\nExperiment {experiment_name} deleted")

listOfExperiments = list_sagemaker_experiments()

# Use experiment name not display name
# loop through each experiment and delete
for experiment in listOfExperiments:
    cleanup_boto3(experiment)
    print(f"Experiment {experiment} deleted")

