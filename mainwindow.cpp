#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "twitchclient.h"
#include "filemanager.h"
#include "asyncprocessrunner.h"

#include <QSystemTrayIcon>
#include <QProcess>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    init();

}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::init()
{
    ui->raidAmount->setValidator(new QIntValidator(0, 100000, this));
    ui->addFollowersAmount->setValidator(new QIntValidator(0, 100000, this));
    ui->registerAccountsAmount->setValidator(new QIntValidator(0, 100000, this));
}

void MainWindow::on_raidSubmit_clicked()
{
    QString raidAmount      = ui->raidAmount->text();
    QString raidNickname    = ui->raidNickname->text();

    if (raidAmount.size() > 0 && raidNickname.size() > 0) {

        QSystemTrayIcon trayIcon;
        trayIcon.setIcon(QIcon("/Users/timstellar/Documents/Projects/StreamForge/logo.png"));
        trayIcon.show();
        trayIcon.showMessage("Raid started.", "User: " + raidNickname + ", Amount: " + raidAmount + ".", QSystemTrayIcon::Information, 5000);

        QUrl url(QStringLiteral("wss://irc-ws.chat.twitch.tv:443"));

        FileManager proxies("/Users/timstellar/Documents/Projects/StreamForge/proxies.txt");
        FileManager accounts("/Users/timstellar/Documents/Projects/StreamForge/accounts.txt");
        QVector<QStringList> prox = proxies.getData();
        QVector<QStringList> accs = accounts.getData();

        QVector<TwitchClient*> clients;
        for (int i = 0; i < qMin(qMin(accs.size(), prox.size()), raidAmount.toInt()); ++i) {
            TwitchClient *client = new TwitchClient(url, accs.at(i), raidNickname, prox.at(i));
            clients.append(client);

            // QTimer::singleShot(3000, client, [client]() {
            //     client->sendMessage("Привет");
            // });
        }

        AsyncProcessRunner *runner = new AsyncProcessRunner(this);
        connect(runner, &AsyncProcessRunner::processFinished, this, &MainWindow::handleProcessFinished);
        runner->runProcess(raidNickname, raidAmount);

        qDeleteAll(clients);
    }
}

void MainWindow::handleProcessFinished()
{

}

