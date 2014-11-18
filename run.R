td <- read.csv("TestData_asn.csv", header=TRUE, comment.char = "#")
tr <- read.csv("TestRecord_loc.csv", header=TRUE, comment.char = "#")
md <- merge(td, tr, by=c("Key", "RemoteAddr", "GetTime"))

# Drop tables
td <- NULL
tr <- NULL

# Drop columns
md$TrackData.Referer <- NULL
md$TrackData.RequestID <- NULL

# Filter by ASN
mdf <- md
mdf <- mdf[ mdf$TrackData.ASN != 36850, ] # UNC


# Filter address
mdf <- mdf[ mdf$RemoteAddr != "152.2.129.95", ] # dev UNC
mdf <- mdf[ mdf$RemoteAddr != "2620:0:1000:2501:be30:5bff:fee1:b9c", ] # dev Google
mdf <- mdf[ mdf$RemoteAddr != "2620:0:1000:2501:baac:6fff:fe98:c11f", ] # dev Google

# Filter bad values
mdf <- mdf[ mdf$LatencyData.Max > 0, ]
mdf <- mdf[ mdf$LatencyData.Min > 0, ]
mdf <- mdf[ mdf$LatencyData.Med > 0, ]
mdf <- mdf[ mdf$LatencyData.Mean > 0, ]
mdf <- mdf[ mdf$LatencyData.Len >= 10, ]
mdf <- mdf[ mdf$ThroughputData.Max > 0, ]
mdf <- mdf[ mdf$ThroughputData.Min > 0, ]
mdf <- mdf[ mdf$ThroughputData.Med > 0, ]
mdf <- mdf[ mdf$ThroughputData.Mean > 0, ]
mdf <- mdf[ mdf$ThroughputData.Max != Inf, ]
mdf <- mdf[ !is.na(mdf$ThroughputData.Max), ]

write.csv(mdf, file="MergeData.csv", row.names=TRUE)