{% set task = frappe.get_doc("SNM Task", doc.reference_name) %}

<div style="font-family:Segoe UI, Arial, sans-serif;background:#f4f6f9;padding:15px;">

    <table width="100%" cellpadding="0" cellspacing="0"
           style="max-width:600px;
                  margin:auto;
                  background:#ffffff;
                  border:1px solid #e5e7eb;
                  border-radius:8px;">

        <tr>
            <td style="background:#dc2626;padding:15px 20px;">
                <h2 style="margin:0;color:#ffffff;font-size:20px;">
                    ⏰ Task Due Tomorrow
                </h2>
            </td>
        </tr>

        <tr>
            <td style="padding:20px;">

                <p>Hello,</p>

                <p>
                    This is a reminder that the following task is due tomorrow.
                </p>

                <table width="100%" cellpadding="8" cellspacing="0"
                       style="border-collapse:collapse;font-size:14px;">

                    <tr>
                        <td width="140"
                            style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Task Subject
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
                            Priority
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.priority or "-" }}
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
                            Department
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.department or "-" }}
                        </td>
                    </tr>

                    <tr>
                        <td style="background:#f8fafc;border:1px solid #e5e7eb;font-weight:600;">
                            Assigned By
                        </td>
                        <td style="border:1px solid #e5e7eb;">
                            {{ task.allocated_by or "-" }}
                        </td>
                    </tr>

                </table>

                <div style="margin-top:15px;
                            padding:12px;
                            background:#fef2f2;
                            border-left:4px solid #dc2626;
                            color:#7f1d1d;">
                    Please complete this task before the due date.
                </div>

                <div style="text-align:center;margin-top:20px;">
                    <a href="frappe.utis.get_url()/app/snm-task/{{ task.name }}"
                       style="background:#dc2626;
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

            </td>
        </tr>

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