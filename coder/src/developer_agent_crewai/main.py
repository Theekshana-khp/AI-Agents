
import warnings
import os


from developer_agent_crewai.crew import DeveloperAgentCrewai

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

os.makedirs('output', exist_ok=True)

assignment = 'Write a python program to calculate the first 10,000 terms \
    of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...'


def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': assignment,
    }

    result = DeveloperAgentCrewai().crew().kickoff(inputs=inputs)
    print(result.raw)


if __name__ == "__main__":
    run()