<p>{% set task = frappe.get_doc("SNM Task", doc.reference_name) %}</p>

<div style="font-family:Segoe UI, Arial, sans-serif;background:#f4f6f9;padding:15px;">

    <table width="100%" cellpadding="0" cellspacing="0"
        style="max-width:600px;
               margin:auto;
               background:#ffffff;
               border:1px solid #e5e7eb;
               border-radius:8px;
               overflow:hidden;">

        <!-- Header -->
        <tr>
            <td style="background:#1f4e79;padding:15px 20px;">
                <h2 style="margin:0;font-size:20px;color:#ffffff;">
                    📌 New Task Assigned
                </h2>
            </td>
        </tr>

        <!-- Content -->
        <tr>
            <td style="padding:20px;">

                <p style="margin-top:0;color:#374151;font-size:14px;">
                    Hello,
                </p>

                <p style="color:#6b7280;font-size:14px;">
                    A new task has been assigned to you.
                </p>

                <table width="100%" cellpadding="8" cellspacing="0"
                    style="border-collapse:collapse;font-size:14px;">

                    <tr>
                        <td width="140"
                            style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Subject
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.subject }}
                        </td>
                    </tr>

                    <tr>
                        <td style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Description
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.description or "-" }}
                        </td>
                    </tr>

                    <tr>
                        <td style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Start Date
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.start_date or "-" }}
                        </td>
                    </tr>

                    <tr>
                        <td style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Due Date
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.due_date or "-" }}
                        </td>
                    </tr>


                    <tr>
                        <td style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Allocated By
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.allocated_by or "-" }}
                        </td>
                    </tr>

                </table>

                    <div style="text-align:center;margin-top:20px;">
                        <a href="{{ frappe.utils.get_url() }}/app/snm-task/{{ task.name }}"
                            style="background:#1f4e79;
                                   color:#ffffff;
                                   text-decoration:none;
                                   padding:10px 22px;
                                   border-radius:5px;
                                   font-size:14px;
                                   font-weight:600;
                                   display:inline-block;">
                            Open Task
                        </a>
                    </div>

                <div style="margin-top:18px;
                            padding:10px;
                            background:#eff6ff;
                            border-left:3px solid #2563eb;
                            font-size:13px;
                            color:#374151;">
                    Please review the task and update its progress regularly.
                </div>

            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td style="background:#f9fafb;
                       padding:12px;
                       text-align:center;
                       font-size:11px;
                       color:#6b7280;">
                Meeting Management System
            </td>
        </tr>

    </table>

</div>
