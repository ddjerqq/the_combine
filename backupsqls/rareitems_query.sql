DROP TABLE IF EXISTS Temp_Apeerance;
DROP TABLE IF EXISTS hape_with_nulls;



CREATE TABLE hape_with_nulls
AS
SELECT h.name, ha.attribute_type, hap.attribute_value
FROM (SELECT distinct(name) FROM hape) as h
CROSS JOIN (SELECT DISTINCT(attribute_type) FROM hape) as ha
LEFT JOIN hape hap ON h.name = hap.name and ha.attribute_type = hap.attribute_type;

INSERT INTO hape VALUES(NULL, 'Traits count', NULL);

UPDATE hape_with_nulls
SET attribute_value = name
where attribute_value is NULL;

CREATE TABLE Temp_Apeerance
AS
select       attribute_value,
       count(attribute_value)  Appereance,
       count(*) OVER (PARTITION BY NULL) AS Total
FROM hape_with_nulls as h
GROUP BY attribute_value;

SELECT h.name, 1/exp(SUM(log((TA.Appereance / CAST(TA.Total AS FLOAT))))) AS SCORE
FROM hape_with_nulls as h
LEFT JOIN Temp_Apeerance as TA ON h.attribute_value=TA.attribute_value
GROUP BY h.name
ORDER BY SCORE DESC;


