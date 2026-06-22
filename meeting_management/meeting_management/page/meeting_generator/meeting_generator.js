// meeting_management/meeting_management/page/meeting_generator/meeting_generator.js

frappe.pages['meeting-generator'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Meeting Scheduler',
        single_column: true
    });

    $(page.body).html(`
        <div class="employee-card">
            <table class="employee-table">
                <thead>
                    <tr>
                        <th style="width: 100px;">Sr. No</th>
                        <th>USER NAME</th>
                        <th>EMAIL ID</th>
                        <th style="text-align: center; width: 220px;">ACTION</th>
                    </tr>
                </thead>
                <tbody id="meeting_user_body">
                    <tr>
                        <td colspan="4" class="text-center" style="padding: 30px; color: #6b7280;">
                            Loading available hosts...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    `);

    // CSS Styling to match your provided image exactly
    $(page.body).append(`
        <style>
            .employee-card {
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            .employee-table {
                width: 100%;
                border-collapse: collapse;
            }
            .employee-table th {
                background: #f8fafc;
                padding: 12px 20px;
                text-align: left;
                font-weight: 600;
                color: #64748b;
                font-size: 12px;
                letter-spacing: 0.05em;
                border-bottom: 1px solid #edf2f7;
            }
            .employee-table td {
                padding: 16px 20px;
                border-bottom: 1px solid #f1f5f9;
                font-size: 14px;
                color: #1e293b;
                vertical-align: middle;
            }
            .employee-table tr:hover {
                background: #f8fafc;
            }
            .user-link {
                color: #1e293b;
                font-weight: 700;
                text-decoration: none;
                cursor: pointer;
            }
            .user-link:hover {
                text-decoration: underline;
                color: #008000;
            }
            .btn-schedule-green {
                background-color: #008000; /* Dark Green */
                color: white !important;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
                width: 100%;
            }
            .btn-schedule-green:hover {
                background-color: #006400;
            }
            .text-center { text-align: center; }
        </style>
    `);

    // Redirection function shared by name link and button
    window.schedule_with_user = function(user_id) {
        frappe.call({
            method: "meeting_management.meeting_management.page.meeting_generator.meeting_generator.get_user_scheduler_url",
            args: { user: user_id },
            callback: function(r) {
                if (r.message) {
                    window.open(r.message, "_blank");
                }
            }
        });
    };

    // Load user data
    frappe.call({
        method: "meeting_management.meeting_management.page.meeting_generator.meeting_generator.get_simple_user_list",
        callback: function(r) {
            let html = "";
            if (r.message && r.message.length) {
                r.message.forEach((user, index) => {
                    html += `
                        <tr>
                            <td style="color: #94a3b8;">${index + 1}</td>
                            <td>
                                <a class="user-link" onclick="schedule_with_user('${user.name}')">
                                    ${user.full_name || user.name}
                                </a>
                            </td>
                            <td style="color: #64748b;">${user.name}</td>
                            <td>
                                <button class="btn-schedule-green" onclick="schedule_with_user('${user.name}')">
                                    Schedule Appointment
                                </button>
                            </td>
                        </tr>
                    `;
                });
            } else {
                html = '<tr><td colspan="4" class="text-center">No available hosts found.</td></tr>';
            }
            $("#meeting_user_body").html(html);
        }
    });
};