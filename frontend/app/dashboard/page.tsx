/*
    Author: Sean Collins
    Copyright: 2026
*/
import { redirect } from "next/navigation";

/**
 * Sets dashboard home as default page when opening dashboard.
 */
export default function Redirect() {
    redirect('/dashboard/home');
}