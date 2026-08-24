<div style="
    font-family: Arial, sans-serif;
    background: #f4f6f9;
    padding: 25px;
">

    <div style="
        max-width: 600px;
        margin: auto;
        background: #ffffff;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    ">

        <!-- Header -->
        <div style="
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            padding: 28px;
            color: white;
            text-align: center;
        ">
            <h2 style="
                margin: 0;
                font-size: 26px;
                font-weight: 700;
            ">
                Meeting Scheduled
            </h2>

            <p style="
                margin-top: 10px;
                font-size: 14px;
                opacity: 0.95;
            ">
                A new meeting has been successfully scheduled
            </p>
        </div>

        <!-- Body -->
        <div style="padding: 30px;">

            <p style="
                margin-top: 0;
                color: #4b5563;
                font-size: 15px;
                line-height: 1.7;
            ">
                Please find the meeting details below:
            </p>

            <!-- Details Card -->
            <div style="
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            ">

                <!-- Date -->
                <div style="
                    padding: 12px 0;
                    border-bottom: 1px dashed #d1d5db;
                ">
                    <div style="
                        color: #6b7280;
                        font-size: 13px;
                        margin-bottom: 4px;
                    ">
                        Meeting Date
                    </div>

                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #111827;
                    ">
                        {{ frappe.utils.formatdate(doc.meeting_from) }}
                    </div>
                </div>

                <!-- From -->
                <div style="
                    padding: 12px 0;
                    border-bottom: 1px dashed #d1d5db;
                ">
                    <div style="
                        color: #6b7280;
                        font-size: 13px;
                        margin-bottom: 4px;
                    ">
                        From Time
                    </div>

                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #4f46e5;
                    ">
                        {{ doc.meeting_from }}
                    </div>
                </div>

                <!-- To -->
                <div style="
                    padding: 12px 0;
                    {% if meeting_arranged_by %}border-bottom: 1px dashed #d1d5db;{% endif %}
                ">
                    <div style="
                        color: #6b7280;
                        font-size: 13px;
                        margin-bottom: 4px;
                    ">
                        To Time
                    </div>

                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #4f46e5;
                    ">
                        {{ doc.meeting_to }}
                    </div>
                </div>

                {% if meeting_arranged_by %}
                <!-- Arranged By -->
                <div style="padding-top: 12px;">

                    <div style="
                        color: #6b7280;
                        font-size: 13px;
                        margin-bottom: 4px;
                    ">
                        Meeting Arranged By
                    </div>

                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #111827;
                    ">
                        {{ doc.meeting_arranged_by }}
                    </div>

                </div>
                {% endif %}
                <div style="padding-top: 12px;">

                    <div style="
                        color: #6b7280;
                        font-size: 13px;
                        margin-bottom: 4px;
                    ">
                        Meeting Link
                    </div>

                    <div style="
                        font-size: 16px;
                        font-weight: 600;
                        color: #111827;
                    ">
                        <a href='{{doc.meet_link}}'>{{doc.meet_link}}</a>
                    </div>

                </div>

            </div>

        </div>

        <!-- Footer -->
        <div style="
            text-align: center;
            padding: 18px;
            background: #f9fafb;
            color: #6b7280;
            font-size: 12px;
        ">
        </div>

    </div>

</div>