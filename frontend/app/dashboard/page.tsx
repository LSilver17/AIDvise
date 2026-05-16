/*=============================================================================
CSC 212 — AI Academic Advising Platform
Copyright (c) 2026 Quinsigamond Community College — CSC 212
All rights reserved.
Author:   Sean Collins
GitHub:   https://github.com/LSilver17/CSC212---AI-Agent
=============================================================================*/
import { redirect } from "next/navigation";

/**
 * Sets dashboard home as default page when opening dashboard.
 */
export default function Redirect() {
    redirect('/dashboard/home');
}