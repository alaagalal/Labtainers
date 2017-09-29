/*
 * Licensed to Green Energy Corp (www.greenenergycorp.com) under one or
 * more contributor license agreements. See the NOTICE file distributed
 * with this work for additional information regarding copyright ownership.
 * Green Energy Corp licenses this file to you under the Apache License,
 * Version 2.0 (the "License"); you may not use this file except in
 * compliance with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * This project was forked on 01/01/2013 by Automatak, LLC and modifications
 * may have been made to this file. Automatak, LLC licenses these modifications
 * to you under the terms of the License.
 */
#include "EmptyResponseTask.h"

#include "opendnp3/master/TaskPriority.h"

using namespace openpal;

namespace opendnp3
{

EmptyResponseTask::EmptyResponseTask(const std::shared_ptr<TaskContext>& context, IMasterApplication& app, const std::string& name, FunctionCode func, const std::function<bool(HeaderWriter&)>& format, openpal::MonotonicTimestamp startExpiration, openpal::Logger logger, const TaskConfig& config) :
	IMasterTask(context, app, TaskBehavior::SingleExecutionNoRetry(startExpiration), logger, config),
	name(name),
	func(func),
	format(format)
{

}

bool EmptyResponseTask::EmptyResponseTask::BuildRequest(APDURequest& request, uint8_t seq)
{
	request.SetControl(AppControlField(true, true, false, false, seq));
	request.SetFunction(this->func);
	auto writer = request.GetWriter();
	return format(writer);
}

/*func, priority::USER_REQUEST, format*/

IMasterTask::ResponseResult EmptyResponseTask::ProcessResponse(const opendnp3::APDUResponseHeader& header, const openpal::RSlice& objects)
{
	return ValidateNullResponse(header, objects) ? ResponseResult::OK_FINAL : ResponseResult::ERROR_BAD_RESPONSE;
}


} //end ns
