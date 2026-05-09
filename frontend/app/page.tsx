/*
    Author: Sean Collins
    Copyright: 2026
*/
import { redirect } from "next/navigation";

/**
 * Automatically directs users to login page when opening
 * the application.
 */
export default function Redirect() {
    redirect('/login');
}