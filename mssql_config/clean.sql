DECLARE @sql nvarchar(max) = '';

SELECT @sql += 'ALTER TABLE ' + QUOTENAME(t.name) + ' DROP CONSTRAINT ' + QUOTENAME(fk.name) + ';' 
FROM sys.tables AS t JOIN sys.foreign_keys AS fk
ON t.object_id = fk.parent_object_id;

SELECT @sql += 'DROP TABLE ' + QUOTENAME(name) + '; PRINT ''Dropping table: ' + name + ''';'
FROM sys.tables

EXEC sp_executesql @sql;