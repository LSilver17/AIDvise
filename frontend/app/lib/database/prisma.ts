/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Authors:   Prisma, Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
Description:
    Prisma
=============================================================================*/
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3"
import { PrismaClient } from "../../../src/generated/prisma/client"
import data from "../../../../config.json"

const adapter = new PrismaBetterSqlite3({url: `${data.database_config.db_name}.db`});
export const prisma = new PrismaClient({ adapter });
