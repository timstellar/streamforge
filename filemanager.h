#ifndef FILEMANAGER_H
#define FILEMANAGER_H

#include <QObject>
#include <QFile>
#include <QDebug>

class FileManager : public QObject
{
    Q_OBJECT

public:
    FileManager(const QString& fileName);

    QVector<QStringList> getData();

private:
    QFile m_file;
};

#endif // FILEMANAGER_H
