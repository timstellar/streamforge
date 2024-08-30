#include "asyncprocessrunner.h"

void AsyncProcessRunner::runProcess(const QString &raidNickname, const QString &raidAmount)
{
    QProcess *process = new QProcess(this);

    connect(process, &QProcess::readyReadStandardOutput, this, [process]() {
        qDebug() << "Output:" << process->readAllStandardOutput();
    });

    connect(process, &QProcess::readyReadStandardError, this, [process]() {
        qDebug() << "Error:" << process->readAllStandardError();
    });

    connect(process, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            [this, process](int exitCode, QProcess::ExitStatus exitStatus) {
                qDebug() << "Process finished. Exit code:" << exitCode << "Exit status:" << exitStatus;
                process->deleteLater();
                emit processFinished();
            });

    QString command = "/usr/bin/python3";
    QStringList params;
    params << "/Users/timstellar/Documents/Projects/StreamForge/viewer_bot.py";
    params << raidNickname;
    params << raidAmount;

    qDebug() << "Starting command:" << command << params;
    process->start(command, params);
}
