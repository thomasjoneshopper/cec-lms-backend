DECLARE @sql nvarchar(max) = '';

SELECT @sql += 
'SELECT '''' AS ' + t.name + ', * FROM ' + QUOTENAME(t.name) + ';'
FROM sys.tables as t

IF @sql != ''
EXEC sp_executesql @sql;
ELSE 
PRINT 'Tables not found'