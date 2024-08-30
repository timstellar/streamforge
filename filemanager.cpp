#include "filemanager.h"

FileManager::FileManager(const QString &fileName) : m_file(fileName)
{
    if(!m_file.open(QIODevice::ReadOnly)) {
        qDebug() << "File error:" << m_file.errorString();
    }

    m_file.close();
}

QVector<QStringList> FileManager::getData()
{
    QVector<QStringList> data;
    if(!m_file.open(QIODevice::ReadOnly)) {
        qDebug() << "File error:" << m_file.errorString();
    }

    QTextStream in(&m_file);
    while(!in.atEnd()) {
        QString line = in.readLine();
        QStringList info = line.split(":");
        data.append(info);
    }

    m_file.close();
    return data;
}
