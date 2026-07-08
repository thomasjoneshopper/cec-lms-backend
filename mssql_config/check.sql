DECLARE @sql nvarchar(max) = '';

SELECT @sql += 
'SELECT '''' AS ' + t.name + ', * FROM ' + QUOTENAME(t.name) + ';'
FROM sys.tables as t

EXEC sp_executesql @sql;