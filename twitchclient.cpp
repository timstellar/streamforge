#include "twitchclient.h"

TwitchClient::TwitchClient(const QUrl &url, const QStringList& accountData, const QString& targetChannel, const QStringList& proxyData, QObject *parent)
    : QObject(parent), m_webSocket(), m_oauthToken(accountData[1]), m_username(accountData[0]), m_channel(targetChannel)
{

    QNetworkProxy proxy;
    proxy.setType(QNetworkProxy::HttpProxy);
    proxy.setHostName(proxyData.at(0));
    proxy.setPort(proxyData.at(1).toUShort());
    if (proxyData.size() == 4) {
        proxy.setUser(proxyData.at(2));
        proxy.setPassword(proxyData.at(3));
    }
    m_webSocket.setProxy(proxy);

    connect(&m_webSocket, &QWebSocket::connected, this, &TwitchClient::onConnected);
    connect(&m_webSocket, &QWebSocket::disconnected, this, &TwitchClient::onDisconnected);
    connect(&m_webSocket, &QWebSocket::textMessageReceived, this, &TwitchClient::onTextMessageReceived);
    connect(&m_webSocket, QOverload<QAbstractSocket::SocketError>::of(&QWebSocket::errorOccurred), this, &TwitchClient::onError);
    m_webSocket.open(url);
}

void TwitchClient::onConnected()
{
    qDebug() << "WebSocket connected";
    m_webSocket.sendTextMessage(QString("PASS oauth:%1").arg(m_oauthToken));
    m_webSocket.sendTextMessage(QString("NICK %1").arg(m_username));
    m_webSocket.sendTextMessage(QString("JOIN #%1").arg(m_channel));

    connect(&m_pingTimer, &QTimer::timeout, this, &TwitchClient::sendPing);
    m_pingTimer.start(5 * 60 * 1000);
}

void TwitchClient::onDisconnected()
{
    qDebug() << "WebSocket disconnected";
}

void TwitchClient::onTextMessageReceived(QString message)
{
    if (message.contains("PRIVMSG")) {
        int userEnd = message.indexOf('!');
        QString user = message.mid(1, userEnd - 1);

        int msgStart = message.indexOf(" :") + 2;
        QString chatMessage = message.mid(msgStart);

        qDebug() << user << ": " << chatMessage;

        if (chatMessage.contains("trigger_word")) {
            qDebug() << "Trigger word detected!";
        }
    }
}

void TwitchClient::onError(QAbstractSocket::SocketError error)
{
    qDebug() << "WebSocket error:" << error;
}

void TwitchClient::sendPing()
{
    if (m_webSocket.isValid()) {
        m_webSocket.sendTextMessage("PING :tmi.twitch.tv");
        qDebug() << "Sent PING to keep connection alive";
    } else {
        qDebug() << "PING: WebSocket is not connected";
    }
}

void TwitchClient::sendMessage(const QString& message)
{
    if (m_webSocket.isValid()) {
        m_webSocket.sendTextMessage(QString("PRIVMSG #%1 :%2").arg(m_channel, message));
        qDebug() << "Sent message:" << message;
    } else {
        qDebug() << "WebSocket is not connected";
    }
}

TwitchClient::~TwitchClient()
{
    m_webSocket.close();
}
