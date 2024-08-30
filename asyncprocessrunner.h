#ifndef ASYNCPROCESSRUNNER_H
#define ASYNCPROCESSRUNNER_H

#include <QProcess>
#include <QDebug>

class AsyncProcessRunner : public QObject
{
    Q_OBJECT

public:
    AsyncProcessRunner(QObject *parent = nullptr) : QObject(parent) {}

    void runProcess(const QString &raidNickname, const QString &raidAmount);

signals:
    void processFinished();
};

// Usage example:
// AsyncProcessRunner *runner = new AsyncProcessRunner(this);
// connect(runner, &AsyncProcessRunner::processFinished, this, &YourClass::handleProcessFinished);
// runner->runProcess("nickname", "amount");

#endif // ASYNCPROCESSRUNNER_H
