# Import for integration with BotCity Maestro SDK
from botcity.maestro import *


# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    maestro.alert(execution.task_id, "Example Bot started!", AlertType.INFO)

    # Here you can call you main.py file or implement your bot's logic

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Congratulations on finishing first task with success. 🎉"
    )

if __name__ == '__main__':
    main()