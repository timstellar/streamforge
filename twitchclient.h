#ifndef TWITCHCLIENT_H
#define TWITCHCLIENT_H

#include <QObject>
#include <QTimer>
#include <QtWebSockets/QWebSocket>

class TwitchClient : public QObject
{
    Q_OBJECT

public:
    explicit TwitchClient(const QUrl &url, const QStringList& accountData, const QString& targetChannel, const QStringList& proxyData, QObject *parent = nullptr);
    void sendMessage(const QString& message);
    ~TwitchClient();

private slots:
    void onConnected();
    void onDisconnected();
    void onTextMessageReceived(QString message);
    void onError(QAbstractSocket::SocketError error);
    void sendPing();

private:
    QWebSocket m_webSocket;
    QString m_oauthToken;
    QString m_username;
    QString m_channel;
    QTimer m_pingTimer;

signals:
};

#endif // TWITCHCLIENT_H
