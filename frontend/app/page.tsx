/*
    Author: Sean Collins
*/
import { redirect } from "next/navigation";

/**
 * Automatically directs users to login page when opening
 * the application.
 */
export default function Redirect() {
    redirect('/login');
}